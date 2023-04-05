import asyncio
import fcntl
import json

import aiomysql
import redis
import requests_cache
import yaml
from loguru import logger

loop = asyncio.get_event_loop()
config_yaml = yaml.safe_load(open('config.yaml', 'r', encoding='UTF-8'))
try:
    cloud_config_json = json.load(open('cloud.json', 'r', encoding='UTF-8'))
except FileNotFoundError:
    with open('cloud.json', 'w', encoding='UTF-8') as f:
        f.write("""{
  "MySQL_Pwd": "",
  "MySQL_Port": 3306,
  "MySQL_Host": "localhost",
  "MySQL_db": "datebase",
  "Redis_Host": "localhost",
  "Redis_port": 6379
}""")
        logger.error(
            'cloud.json 未创建，程序已自动创建，请参考 https://github.com/daizihan233/KuoHuBit/issues/17 填写该文件的内容')
        exit(1)
try:
    dyn_yaml = yaml.safe_load(open('dynamic_config.yaml', 'r', encoding='UTF-8'))
except FileNotFoundError:
    with open('dynamic_config.yaml', 'w', encoding='UTF-8') as f:
        f.write("""mute:
- null
word:
- null""")
        logger.warning('dynamic_config.yaml 已被程序自动创建')


def get_config(name: str):
    try:
        return config_yaml[name]
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def get_cloud_config(name: str):
    try:
        return cloud_config_json[name]
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def get_dyn_config(name: str):
    try:
        return dyn_yaml[name]
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def safe_file_read(filename: str, encode: str = "UTF-8", mode: str = "r") -> str or bytes:
    if mode == 'r':
        with open(filename, mode, encoding=encode) as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)
            tmp = file.read()
        return tmp
    if mode == 'rb':
        with open(filename, mode) as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)
            tmp = file.read()
        return tmp


def safe_file_write(filename: str, s, mode: str = "w", encode: str = "UTF-8"):
    if 'b' not in mode:
        with open(filename, mode, encoding=encode) as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)
            file.write(s)
    else:
        with open(filename, mode) as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)
            file.write(s)


async def select_fetchone(sql, arg=None):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

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
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    result = await cur.fetchall()
    await cur.close()
    conn.close()
    return result


async def run_sql(sql, arg):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    await cur.execute(sql, arg)
    await cur.execute("commit")
    await cur.close()
    conn.close()


backend = requests_cache.RedisCache(host=get_cloud_config('Redis_Host'), port=get_cloud_config('Redis_port'))
session = requests_cache.CachedSession("global_session", backend=backend, expire_after=360)

p = redis.ConnectionPool(host=get_cloud_config('Redis_Host'), port=get_cloud_config('Redis_port'))
r = redis.Redis(connection_pool=p, decode_responses=True)
