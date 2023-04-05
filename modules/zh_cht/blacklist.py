#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import asyncio

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from loguru import logger

import botfunc

channel = Channel.current()
channel.name("黑名单")
channel.description("屌你老母")
channel.author("HanTools")
loop = asyncio.get_event_loop()


async def get_all_admin() -> list:
    tmp = await botfunc.select_fetchall("SELECT uid FROM admin")
    t = []
    for i in tmp:
        t.append(i[0])
    logger.debug(t)
    return list(t)


async def get_all_sb() -> list:
    tmp = await botfunc.select_fetchall('SELECT uid FROM blacklist')
    t = []
    for i in tmp:
        t.append(i[0])
    return t


@listen(GroupMessage)
async def nmms(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("刪黑")):
    admins = await get_all_admin()
    if event.sender.id not in admins:
        return
    try:
        await botfunc.run_sql('DELETE FROM blacklist WHERE uid = %s',
                              (int(str(message)),))
        await app.send_message(event.sender.group, "好了！")
    except Exception as err:
        await app.send_message(event.sender.group, f"Umm，{err}")
