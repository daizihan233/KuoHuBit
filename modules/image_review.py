#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import base64
import hashlib
import json

import yaml
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.ims.v20201229 import ims_client, models

import botfunc
import depen

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "图片审核"
channel.meta["description"] = "你疑似有点太极端了"
channel.meta["author"] = "KuoHu"
dyn_config = "dynamic_config.yaml"


async def using_tencent_cloud(content: str, user_id: str) -> dict:
    if botfunc.r.hexists("imgsafe", hashlib.sha384(content.encode()).hexdigest()):
        return json.loads(
            botfunc.r.hget("imgsafe", hashlib.sha384(content.encode()).hexdigest())
        )
    try:
        cred = credential.Credential(
            botfunc.get_cloud_config("QCloud_Secret_id"),
            botfunc.get_cloud_config("QCloud_Secret_key"),
        )
        client = ims_client.ImsClient(cred, "ap-guangzhou")
        req = models.ImageModerationRequest()
        params = {
            "BizType": botfunc.get_cloud_config("img_biztype"),
            "FileContent": content,  # base64
            "User": {"UserId": user_id, "AccountType": "2"},
        }
        req.from_json_string(json.dumps(params))
        resp = client.ImageModeration(req)
        botfunc.r.hset(
            "imgsafe",
            hashlib.sha384(content.encode()).hexdigest(),
            json.dumps(
                {
                    "Suggestion": resp.Suggestion,
                    "SubLabel": resp.SubLabel,
                    "DataId": resp.RequestId,
                }
            )
        )
        botfunc.r.hset(
            "imgsafe",
            resp.RequestId,
            hashlib.sha384(content.encode()).hexdigest()
        )
        logger.debug(f"新图片入库！{resp.Suggestion} | {resp.SubLabel} | {resp.RequestId}")
        return {
            "Suggestion": resp.Suggestion,
            "SubLabel": resp.SubLabel,
            "DataId": resp.RequestId,
        }
    except TencentCloudSDKException as err:
        logger.error(err)
    return {"Suggestion": "Pass", "SubLabel": "", "DataId": ""}


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("图片审核，启动！"), depen.check_authority_bot_op()],
    )
)
async def start_review(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, "r") as cf:
        cfy = yaml.safe_load(cf)
    cfy["img"].append(group.id)
    cfy["img"] = list(set(cfy["img"]))
    with open(dyn_config, "w") as cf:
        yaml.dump(cfy, cf)
    await app.send_message(group, MessageChain([At(event.sender.id), Plain(" OK辣！")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("图片审核，卸载！"), depen.check_authority_bot_op()],
    )
)
async def stop_review(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, "r") as cf:
        cfy = yaml.safe_load(cf)
    try:
        cfy["img"].remove(group.id)
        cfy["img"] = list(set(cfy["img"]))
        with open(dyn_config, "w") as cf:
            yaml.dump(cfy, cf)
        await app.send_message(
            group, MessageChain([At(event.sender.id), Plain(" OK辣！")])
        )
    except Exception as err:
        await app.send_message(
            group, MessageChain([At(event.sender.id), Plain(f" 报错辣！{err}")])
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[depen.match_image(), depen.check_authority_member()],
    )
)
async def image_review(app: Ariadne, message: MessageChain, event: GroupMessage):
    if event.sender.group.id in botfunc.get_dyn_config("img"):
        for i in message[Image]:
            data = await i.get_bytes()
            result = await using_tencent_cloud(
                base64.b64encode(data).decode(), str(event.sender.id)
            )
            logger.debug(result)
            if result["Suggestion"] == "Block":
                await app.recall_message(event.source, event.sender.group)
                await app.send_message(
                    event.sender.group,
                    MessageChain(
                        [
                            At(event.sender.id),
                            Plain(
                                " 你疑似有点太极端了\n"
                                f"识别标签：{result['SubLabel']}\n"
                                f"数据编码：{result['DataId']}\n"
                                f"\n"
                                f"**当你认为这是误判请提供【数据编码】给机器人账号所有者**\n"
                                f"【数据来源：腾讯云图片内容安全】\n"
                                f"本机器人所有者为：{await botfunc.get_su()}（来自配置文件）\n"
                            ),
                        ]
                    ),
                )
