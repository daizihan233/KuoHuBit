#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel

import botfunc
import cache_var

channel = Channel.current()
channel.name("6榜")
channel.description("666")
channel.author("HanTools")


@listen(GroupMessage)
@decorate(MatchContent("6，閉嘴"))
async def no_six(app: Ariadne, group: Group, event: GroupMessage):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    if group.id not in cache_var.no_6:
        cache_var.no_6.append(group.id)
        await botfunc.run_sql("""INSERT INTO no_six VALUES (%s)""", (group.id,))
        await app.send_group_message(
            group,
            MessageChain(
                [
                    At(event.sender.id),
                    Plain(" 好啊，很好啊")
                ]
            ),
            quote=event.source
        )


@listen(GroupMessage)
@decorate(MatchContent("6，張嘴"))
async def yes_six(app: Ariadne, group: Group, event: GroupMessage):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    if group.id in cache_var.no_6:
        cache_var.no_6.remove(group.id)
        await botfunc.run_sql("""DELETE FROM no_six WHERE gid = %s""", (group.id,))
        await app.send_group_message(
            group,
            MessageChain(
                [
                    At(event.sender.id),
                    Plain(" 好啊，很好啊")
                ]
            ),
            quote=event.source
        )
