#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import asyncio

import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("来份涩图")
channel.description("人类有三大欲望……")
channel.author("HanTools")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("涩图来")],
    )
)
async def test(app: Ariadne, group: Group, event: GroupMessage):
    # 涩图不一样，这里不能使用缓存
    data = requests.get(botfunc.get_config('setu_api')).content
    b_msg = await app.send_group_message(group, MessageChain(Image(data_bytes=data)))
    await asyncio.sleep(botfunc.get_config('recall'))
    await app.recall_message(b_msg)
    await app.send_message(
        group,
        MessageChain([At(event.sender.id), Plain(" 看完了吗？我撤回了")]),
    )
