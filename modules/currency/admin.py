#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import asyncio

import aiomysql
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from loguru import logger

import botfunc

channel = Channel.current()
channel.name("管理员")
channel.description("114514")
channel.author("HanTools")
loop = asyncio.get_event_loop()


async def select_fetchone(sql, arg=None):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    r = await cur.fetchone()
    await cur.close()
    conn.close()
    return r


async def select_fetchall(sql, arg=None):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return r


async def get_all_admin() -> list:
    tmp = await select_fetchall("SELECT uid FROM admin")
    t = []
    for i in tmp:
        t.append(i[0])
    logger.debug(t)
    return list(t)


async def else_sql(sql, arg):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    await cur.execute(sql, arg)
    await cur.execute("commit")
    await cur.close()
    conn.close()


@listen(GroupMessage)
async def add_admin(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain = DetectPrefix("上管")):
    admins = await get_all_admin()
    if event.sender.id not in admins:
        return
    try:
        await else_sql("INSERT INTO admin(uid) VALUES (%s)", (int(str(message)),))
    except Exception as err:
        await app.send_message(group, f"寄！{err}")
    else:
        await app.send_message(group, f"OK!")


@listen(GroupMessage)
async def add_admin(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain = DetectPrefix("去管")):
    admins = await get_all_admin()
    if event.sender.id not in admins:
        return
    try:
        await else_sql("DELETE FROM admin WHERE uid = %s", (int(str(message)),))
    except Exception as err:
        await app.send_message(group, f"寄！{err}")
    else:
        await app.send_message(group, f"OK!")
