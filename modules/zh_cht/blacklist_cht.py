#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.util.saya import listen
from graia.saya import Channel

import botfunc

channel = Channel.current()
channel.name("黑名单")
channel.description("屌你老母")
channel.author("HanTools")


@listen(GroupMessage)
async def nmms(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("刪黑")):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    try:
        await botfunc.run_sql('DELETE FROM blacklist WHERE uid = %s',
                              (int(str(message)),))
        await app.send_message(event.sender.group, "好了！")
    except Exception as err:
        await app.send_message(event.sender.group, f"Umm，{err}")
