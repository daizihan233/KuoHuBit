#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta

import depen

channel = Channel[ChannelMeta].current()
channel.meta['name'] = "管理"
channel.meta['description'] = "某种意义上，是种提权？"
channel.meta['author'] = "KuoHu"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            DetectPrefix("禁言 "),
            depen.check_authority_op()
        ]
    )
)
async def fish(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("禁言 ")):
    msg = message.include(At, Plain)
    time = None
    result = ''
    for m in msg:
        if isinstance(m, At):
            if time is not None:
                try:
                    await app.mute_member(group, m.target, time)
                    result += f"{m.target} | 禁言 {time / 60} 分钟 | 成功\n"
                except PermissionError:
                    result += f"{m.target} | 禁言 {time / 60} 分钟 | 错误：【无权限】\n"
            else:
                try:
                    await app.mute_member(group, m.target, 60)
                    result += f"{m.target} | 禁言 1 分钟 | 警告：【语法错误】\n"
                except PermissionError:
                    result += f"{m.target} | 禁言 1 分钟 | 错误：【无权限】\n"
        else:
            try:
                time = int(str(m).lstrip(' ').rstrip(' ')) * 60
            except ValueError:
                pass
    await app.send_group_message(group, result)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            DetectPrefix("踢出 "),
            depen.check_authority_op()
        ]
    )
)
async def fish(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("踢出 ")):
    msg = message.include(At)
    m: At
    result = ''
    for m in msg:
        try:
            await app.kick_member(group, m.target)
            result += f"{m.target} | 已踢出\n"
        except PermissionError:
            result += f"{m.target} | 错误：【无权限】\n"
    await app.send_group_message(group, result)
