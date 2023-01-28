#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import json

import opencc
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel

import botfunc

channel = Channel.current()
channel.name("摸魚日記")
channel.description("上班是不可能上班的~")
channel.author("HanTools")
opc = opencc.OpenCC('s2t')


@listen(GroupMessage)
@decorate(MatchContent("魚"))
async def fish(app: Ariadne, group: Group, event: GroupMessage):
    data: str = json.loads(botfunc.session.get("http://bjb.yunwj.top/php/mo-yu/php.php").text)['wb']
    data: str = data.replace('【换行】', '\n')
    await app.send_message(
        group,
        MessageChain([At(event.sender.id), Plain(f" \n{opc.convert(data)}")]),
    )
