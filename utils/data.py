#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
from loguru import logger

from utils.config import get_config
from utils.sql import select_fetchall


async def get_all_admin() -> list:
    tmp = await select_fetchall("SELECT uid FROM admin")
    t = []
    for i in tmp:
        t.append(i[0])
    logger.debug(t)
    return list(t)


async def get_all_sb() -> list:
    tmp = await select_fetchall("SELECT uid FROM blacklist")
    t = []
    for i in tmp:
        t.append(i[0])
    return t


async def get_su() -> int:
    return get_config("su")
