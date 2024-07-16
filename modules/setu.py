#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import asyncio
import os
import random
import shutil
import time

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.saya.channel import ChannelMeta
from loguru import logger

from utils.config import get_config
from utils.file import safe_file_write, safe_file_read

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "来份涩图"
channel.meta["description"] = "人类有三大欲望……"
channel.meta["author"] = "KuoHu"


async def get_one():
    p = get_config("setu_api2_probability")
    ch = random.randint(1, p)
    if ch == p:
        url = get_config("setu_api2")
    else:
        url = get_config("setu_api")
    logger.info(f"使用URL：{url}（p={p}, ch={ch}, (ch == p)={ch == p}）")
    # 涩图不一样，这里不能使用缓存
    session = Ariadne.service.client_session
    async with session.get(url) as response:
        data = await response.read()
    return data


@listen(GroupMessage)
@decorate(MatchContent("涩图来"))
async def setu(app: Ariadne, group: Group):
    data = await get_one()
    b_msg = await app.send_group_message(group, MessageChain(Image(data_bytes=data)))
    await asyncio.sleep(get_config("recall"))
    await app.recall_message(b_msg)


@listen(GroupMessage)
@decorate(MatchContent("无内鬼，来点加密压缩包"))
async def setu_7z(app: Ariadne, group: Group):
    img_id = time.time()
    await app.send_message(group, f"[{img_id}] 装弹中……")
    fdir = f"./work/{img_id}"
    os.makedirs(fdir)
    for index in range(10):
        data = await get_one()
        safe_file_write(filename=f"{fdir}/{index}.png", mode="wb", s=data)
    os.system(f"7z a {fdir}/res.7z {fdir} -p{group.id}")
    await app.send_message(group, f"[{img_id}] 发射中……")
    await app.upload_file(
        data=safe_file_read(f"{fdir}/res.7z", mode="rb"),
        target=group,
        name=f"s{time.time()}.7z",
    )
    await asyncio.sleep(600)
    shutil.rmtree(fdir)
