#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import time
import urllib.parse

import yaml
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import MemberUnmuteEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group, Member, MemberPerm
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

import botfunc
from botfunc import r

channel = Channel.current()
channel.name("防刷屏")
channel.description("人类可真无聊")
channel.author("HanTools")
dyn_config = 'dynamic_config.yaml'
hash_name = "bot_repeat_record"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def repeat_record(app: Ariadne, group: Group, member: Member, message: MessageChain):
    if group.id in botfunc.get_dyn_config('mute'):
        limit_time = 300  # 5 分钟（5s * 60s = 300s）
        if r.hexists(hash_name, f"{group.id},{member.id}"):
            td = r.hget(hash_name, f"{group.id},{member.id}")
            td = str(td).split(',')
            if str(message) == urllib.parse.unquote(td[2]):
                if time.time() - float(td[1]) < limit_time:
                    r.hset(hash_name, f'{group.id},{member.id}',
                           f"{int(td[0]) + 1},{time.time()},{urllib.parse.quote(str(message))}")  # 这里使用 URLEncode 防止注入
                    if int(td[0]) + 1 > 5:
                        try:
                            await app.mute_member(group, member, limit_time)
                            await app.send_message(group, MessageChain(Plain("boom！一声枪响之后，"), At(member.id),
                                                                       Plain(f' 被禁言了 {limit_time} 秒')))
                        except PermissionError:
                            logger.warning(f'机器人权限过低，无法禁言 {member.id}')
                else:
                    r.hset(hash_name, f'{group.id},{member.id}', f"1,{time.time()},{urllib.parse.quote(str(message))}")
            else:
                r.hset(hash_name, f'{group.id},{member.id}', f"1,{time.time()},{urllib.parse.quote(str(message))}")
        else:
            r.hset(hash_name, f'{group.id},{member.id}', f"1,{time.time()},{urllib.parse.quote(str(message))}")


@listen(GroupMessage)
@decorate(MatchContent("开启本群防刷屏"))
async def start_mute(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    cfy['mute'].append(group.id)
    cfy['mute'] = list(set(cfy["mute"]))
    with open(dyn_config, 'w') as cf:
        yaml.dump(cfy, cf)
    await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK辣！")))


@listen(GroupMessage)
@decorate(MatchContent("关闭本群防刷屏"))
async def stop_mute(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        with open(dyn_config, 'r') as cf:
            cfy = yaml.safe_load(cf)
        try:
            cfy['mute'].remove(group.id)
            cfy['mute'] = list(set(cfy["mute"]))
            with open(dyn_config, 'w') as cf:
                yaml.dump(cfy, cf)
            await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK辣！")))
        except Exception as err:
            await app.send_message(group, MessageChain(At(event.sender.id), Plain(f" 报错辣！{err}")))


@channel.use(
    ListenerSchema(
        listening_events=[MemberUnmuteEvent]
    )
)
async def un_mute(group: Group, member: Member):
    r.hdel(hash_name, f'{group.id},{member.id}')
