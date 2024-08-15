#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import asyncio
import sqlite3

import aiomysql
import pymysql

import utils.var
from utils.config import get_cloud_config

loop = asyncio.get_event_loop()
SQL_DB_NAME = "data.db"


async def select_fetchone(sql, arg=None):
    if utils.var.DB_MODE == utils.var.SQLITE:
        conn = sqlite3.connect(SQL_DB_NAME)
        if arg:
            result = conn.execute(sql.replace("%s", "?"), arg).fetchone()
        else:
            result = conn.execute(sql).fetchone()
        conn.close()
        return result
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
    if utils.var.DB_MODE == utils.var.SQLITE:
        conn = sqlite3.connect(SQL_DB_NAME)
        if arg:
            result = conn.execute(sql.replace("%s", "?"), arg).fetchall()
        else:
            result = conn.execute(sql).fetchall()
        conn.close()
        return result
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


async def run_sql(sql: str, arg=None):
    if utils.var.DB_MODE == utils.var.SQLITE:
        conn = sqlite3.connect(SQL_DB_NAME)
        if arg:
            conn.execute(sql.replace("%s", "?"), arg)
        else:
            conn.execute(sql)
        conn.commit()
        conn.close()
        return 
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


def sync_run_sql(sql, arg=None):
    conn = pymysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        database=get_cloud_config("MySQL_db"),
    )
    cur = conn.cursor()
    if arg:
        cur.execute(sql, arg)
    else:
        cur.execute(sql)
    cur.execute("commit")
    cur.close()
    conn.close()


def sync_select_fetchone(sql, arg=None):
    conn = pymysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        database=get_cloud_config("MySQL_db"),
    )
    cur = conn.cursor()
    if arg:
        cur.execute(sql, arg)
    else:
        cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result


def sync_select_fetchall(sql, arg=None):
    conn = pymysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        database=get_cloud_config("MySQL_db"),
    )
    cur = conn.cursor()
    if arg:
        cur.execute(sql, arg)
    else:
        cur.execute(sql)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
