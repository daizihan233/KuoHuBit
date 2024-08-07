#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import asyncio

import aiomysql

from utils.config import get_cloud_config

loop = asyncio.get_event_loop()


async def select_fetchone(sql, arg=None):
    conn = await aiomysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        db=get_cloud_config("MySQL_db"),
        loop=loop,
    )

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    result = await cur.fetchone()
    await cur.close()
    conn.close()
    return result


async def select_fetchall(sql, arg=None):
    conn = await aiomysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        db=get_cloud_config("MySQL_db"),
        loop=loop,
    )

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    result = await cur.fetchall()
    await cur.close()
    conn.close()
    return result


async def run_sql(sql, arg=None):
    conn = await aiomysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        db=get_cloud_config("MySQL_db"),
        loop=loop,
    )

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    await cur.execute("commit")
    await cur.close()
    conn.close()
