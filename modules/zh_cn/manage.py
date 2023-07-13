from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen
from graia.saya import Channel

channel = Channel.current()
channel.name("管理")
channel.description("某种意义上，是种提权？")
channel.author("HanTools")


@listen(GroupMessage)
async def fish(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("禁言 ")):
    msg = message.include(At, Plain)
    time = None
    for m in msg:
        if isinstance(m, At):
            if time is not None:
                await app.mute_member(group, m.target, time)
        else:
            try:
                time = int(str(m).lstrip(' ').rstrip(' ')) * 60
            except ValueError:
                pass


@listen(GroupMessage)
async def fish(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("踢出 ")):
    msg = message.include(At)
    m: At
    for m in msg:
        await app.kick_member(group, m.target)
