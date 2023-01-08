#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from main import saya

channel = Channel.current()
channel.name("Menu 菜单")
channel.description("会员制菜单（不是")
channel.author("HanTools")

# 初始化菜单
n = 0
menu_lst = [
    "具体用法见文档：https://botdoc.hantools.top\n"
]
for _, c in saya.channels.items():
    n += 1
    menu_lst.append(f"{n}：{c.meta['name']}")
menu_str = "\n".join(menu_lst)
del n, menu_lst


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("菜单")]
    )
)
async def menu(app: Ariadne, group: Group):
    await app.send_message(
        group,
        MessageChain(
            Plain(menu_str)
        )
    )
