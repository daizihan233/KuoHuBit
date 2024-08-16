import datetime
import random

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.message.parser.base import MentionMe, DetectPrefix
from graia.ariadne.model import Group, Member, Friend
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta
from graiax.text2img.playwright import HTMLRenderer, convert_md, PageOption, ScreenshotOption
from loguru import logger
from openai import AsyncOpenAI
from tokencost.costs import calculate_cost_by_tokens

from utils import depen, var
from utils.config import get_cloud_config, get_config
from utils.data import get_su
from utils.sql import run_sql, sync_run_sql, sync_select_fetchall

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "NyaGPT"
channel.meta["description"] = "喵喵喵？"
channel.meta["author"] = "KuoHu"
# 提示词，在你清楚它是什么之前请不要随意修改
cue = get_config("cue")
messages = {}
tips = get_config("tips")
client = AsyncOpenAI(
    api_key=get_cloud_config("gptkey"),
    base_url=get_cloud_config("gptapi")
)
NOT_GPT_REPLY = "本消息非 GPT 回复"
MODULE_LIST = get_config("model")

sync_run_sql(
    """CREATE TABLE IF NOT EXISTS `cue` ( 
`ids` int UNSIGNED NOT NULL,
`words` VARCHAR(2000) NOT NULL,
`status` BOOLEAN NOT NULL,
`who` INT UNSIGNED NOT NULL
)"""
)
for ids, words, status, who in [x for x in sync_select_fetchall("SELECT ids, words, status, who FROM cue")]:
    var.cue[ids] = words
    var.cue_status[ids] = status
    var.cue_who[ids] = who
class MessageNode:
    """
    消息节点对象
    """

    def __init__(self, message: MessageChain, uid: int, root=None, next_node=None):
        self.message: MessageChain = message
        self.uid: int = uid
        self.root: MessageNode = root
        self.next_node: MessageNode = next_node
        self.index: MessageNode = self

    def __iter__(self):
        self.index = self
        return self

    def __next__(self):
        if self.index.root is None:
            raise StopIteration
        self.index = self.index.root
        return self.index


async def chat(module, msg):
    response = await client.chat.completions.create(
        model=module,
        messages=msg
    )
    prompt_token = response.usage.prompt_tokens
    completion_token = response.usage.completion_tokens
    response = response.choices[0].message.content
    msg.append({"role": "assistant", "content": response})
    prompt_cost = calculate_cost_by_tokens(prompt_token, module, "input")
    completion_cost = calculate_cost_by_tokens(completion_token, module, "output")
    image = await HTMLRenderer().render(
        convert_md(response),
        extra_page_option=PageOption(viewport={"width": 840, "height": 10}, device_scale_factor=1.5),
        extra_screenshot_option=ScreenshotOption(type="jpeg", quality=80, scale="device"),
    )
    return prompt_token, completion_token, prompt_cost, completion_cost, response, images


async def req(c: str, name: str, ids: int, message: MessageChain, event: MessageEvent) -> tuple:
    now = datetime.date.today()

    if event.quote is not None and messages.get(event.quote.id, None) is not None:  # 短路
        node = MessageNode(message, ids, messages[event.quote.id])
        if node.root.uid != get_config("qq"):
            return "？（请回复一条由机器人发出的消息）", NOT_GPT_REPLY
    else:
        node = MessageNode(message, ids, None)
    x = []
    for i in node:
        i: MessageNode
        x.append(
            {
                "role": "assistant" if i.uid == get_config("qq") else "user",
                "content": str(i.message)
            }
        )
    x.reverse()
    if c != "":
        msg = [
                  {
                      "role": "system",
                      "content": c.format(
                          date=f"{now.year}/{now.month}/{now.day}",
                          name=name
                      )
                  }
              ] + x + [
                  {
                      "role": "user",
                      "content": str(node.message)
                  }
              ]
    else:
        msg = x + [
            {
                "role": "user",
                "content": str(node.message)
            }
        ]

    logger.debug(msg)
    for module in MODULE_LIST:
        try:
            prompt_token, completion_token, prompt_cost, completion_cost, response, images = await chat(module, msg)
            warn = (f"本次共追溯 {len(msg) - 2} 条历史消息，消耗 {prompt_token + completion_token} token！"
                    f"（约为 {(prompt_cost + completion_cost) * get_config('rate') * 7} 元）\n"
                    f"使用模型：{module}") if get_config("cost") else ""
            break
        except Exception as err:
            logger.error(err)
    if event.quote is not None and messages.get(event.quote.id, None) is not None:
        messages[event.quote.id].next_node = node
    messages[event.id] = node
    try:
        # noinspection PyUnboundLocalVariable
        return response, warn, images
    except UnboundLocalError:  # 在赋值前调用时
        return "所有模型均无法调用，请查看日志", NOT_GPT_REPLY, NOT_GPT_REPLY


async def make_msg_chain(response, warn, img):
    chain = [Plain("\n"), Plain(response)]
    if warn != "" or tips != [None]:
        chain.append(Plain("\n\n\n---\n"))
        if tips != [None]:
            chain.append(Plain(f"开发者注：{random.choice(tips)}\n"))
        if warn != "":
            chain.append(Plain(f"WARN: {warn}"))
    if img != NOT_GPT_REPLY:
        chain.append(Image(data_bytes=img))
    return chain


@listen(GroupMessage)
async def gpt(
        app: Ariadne,
        group: Group,
        member: Member,
        event: GroupMessage,
        message: MessageChain = MentionMe(),
):
    c = var.cue.get(group.id, cue)
    if var.cue.get(group.id, None) is not None and not var.cue_status[group.id]:
        c = cue
    response, warn, img = await req(c, member.name, member.id, message, event)
    m = await app.send_group_message(
        target=group,
        message=MessageChain(
            await make_msg_chain(response, warn, img)
        ),
        quote=event.source,
    )

    if warn != NOT_GPT_REPLY:
        messages[m.source.id] = MessageNode(response, get_config("qq"), messages[event.id])
        messages[event.id].next_node = messages[m.source.id]


@listen(FriendMessage)
async def gpt_f(
        app: Ariadne, friend: Friend, event: FriendMessage, message: MessageChain
):
    if (
            friend.id == await get_su() and
            (
                    message.startswith("deny ") or
                    message.startswith("accept ") or
                    message.startswith("clear ")
            )
    ):
        return
    c = var.cue.get(friend.id, cue)
    if var.cue.get(friend.id, None) is not None and not var.cue_status[friend.id]:
        c = cue
    response, warn, img = await req(c, friend.nickname, friend.id, message, event)
    m = await app.send_friend_message(
        target=friend,
        message=MessageChain(
            await make_msg_chain(response, warn, img)
        ),
        quote=event.source,
    )
    if warn != NOT_GPT_REPLY:
        messages[m.source.id] = MessageNode(response, get_config("qq"), messages[event.id])
        messages[event.id].next_node = messages[m.source.id]


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectPrefix("修改提示词 "), depen.check_authority_op()],
    )
)
async def add(app: Ariadne, member: Member, group: Group, event: GroupMessage,
              message: MessageChain = DetectPrefix("修改提示词 ")):
    await run_sql(
        """REPLACE INTO cue(ids, words, status, who) VALUES(%s, %s, false, %s);""",
        (group.id, str(message), member.id)
    )
    var.cue[group.id] = str(message)
    var.cue_status[group.id] = False
    var.cue_who[group.id] = member.id
    await app.send_group_message(
        target=group,
        message=MessageChain(
            [
                Plain(
                    f"已更新提示词为如下：\n\n{str(message)}\n\n"
                    f"请注意：为避免滥用此提示词已被转发至开发者后台，请等待开发者通过\n\n"
                    "请注意：当提示词中出现当前日期，可使用{date}代替，使用者名称则为{name}"
                )
            ]
        ),
        quote=event.source,
    )
    await app.send_friend_message(
        target=await get_su(),
        message=MessageChain(
            [
                Plain(
                    f"请审核来自 {group.id} 中 {member.id} 的提示词修改请求：\n"
                    f"\n"
                    f"{str(message)}\n"
                    f"\n"
                    f"同意回复：accept {group.id}\n"
                    f"拒绝回复：deny {group.id}"
                )
            ]
        )
    )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        decorators=[DetectPrefix("修改提示词 ")],
    )
)
async def add_f(app: Ariadne, friend: Friend, event: FriendMessage,
                message: MessageChain = DetectPrefix("修改提示词 ")):
    await run_sql(
        """REPLACE INTO cue(ids, words, status, who) VALUES(%s, %s, false, %s);""",
        (friend.id, str(message), friend.id)
    )
    var.cue[friend.id] = str(message)
    var.cue_status[friend.id] = False
    var.cue_who[friend.id] = friend.id
    await app.send_friend_message(
        target=friend,
        message=MessageChain(
            [
                Plain(
                    f"已更新提示词为如下：\n\n{str(message)}\n\n"
                    f"请注意：为避免滥用此提示词已被转发至开发者后台，请等待开发者通过\n\n"
                    "请注意：当提示词中出现当前日期，可使用{date}代替，使用者名称则为{name}"
                )
            ]
        ),
        quote=event.source,
    )
    await app.send_friend_message(
        target=await get_su(),
        message=MessageChain(
            [
                Plain(
                    f"请审核来自 {friend.id} 的提示词修改请求：\n\n{str(message)}\n\n同意回复：accept {friend.id}\n拒绝回复：deny {friend.id}"
                )
            ]
        )
    )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        decorators=[DetectPrefix("accept "), depen.check_friend_su()],
    )
)
async def accept(app: Ariadne, message: MessageChain = DetectPrefix("accept ")):
    var.cue_status[int(str(message))] = True
    await run_sql("""UPDATE cue SET status=true WHERE ids=%s""", int(str(message)))
    messages[int(str(message))] = []
    if int(str(message)) == var.cue_who[int(str(message))]:  # 是私聊
        await app.send_friend_message(
            target=int(str(message)),
            message=MessageChain(
                [Plain("恭喜！已通过审核")]
            )
        )
    else:
        await app.send_group_message(
            target=int(str(message)),
            message=MessageChain(
                [Plain("恭喜！已通过审核")]
            )
        )


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
        decorators=[DetectPrefix("deny "), depen.check_friend_su()],
    )
)
async def deny(app: Ariadne, message: MessageChain = DetectPrefix("deny ")):
    var.cue_status[int(str(message))] = False
    await run_sql("""DELETE FROM cue WHERE ids=%s""", int(str(message)))
    if int(str(message)) == var.cue_who[int(str(message))]:  # 是私聊
        await app.send_friend_message(
            target=int(str(message)),
            message=MessageChain(
                [
                    Plain(
                        f"开发者：我认为你太极端了（提示词没有通过，请修改，具体可询问机器人开发者{await get_su()}）")
                ]
            )
        )
    else:
        await app.send_group_message(
            target=int(str(message)),
            message=MessageChain(
                [
                    Plain(
                        f"开发者：我认为你太极端了（提示词没有通过，请修改，具体可询问机器人开发者{await get_su()}）")
                ]
            )
        )
