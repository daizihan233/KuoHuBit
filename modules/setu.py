#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import asyncio
import os
import random
import time
from asyncio import subprocess

from aiohttp import ClientSession
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("来份涩图")
channel.description("人类有三大欲望……")
channel.author("HanTools")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("涩图来")],
    )
)
async def setu(app: Ariadne, group: Group):
    p = botfunc.get_config('setu_api2_probability')
    ch = random.randint(1, p)
    if ch == p:
        url = botfunc.get_config('setu_api2')
    else:
        url = botfunc.get_config('setu_api')
    print(f'使用URL：{url}（p={p}, ch={ch}, (ch == p)={ch == p}）')
    # 涩图不一样，这里不能使用缓存
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()

    b_msg = await app.send_group_message(group, MessageChain(Image(data_bytes=data)))
    await asyncio.sleep(botfunc.get_config('recall'))
    await app.recall_message(b_msg)


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("无内鬼，来点加密压缩包")],
    )
)
async def setu_7z(app: Ariadne, group: Group):
    fdir = f'./work/{time.time()}'
    os.makedirs(fdir)
    for index in range(10):
        p = botfunc.get_config('setu_api2_probability')
        ch = random.randint(1, p)
        if ch == p:
            url = botfunc.get_config('setu_api2')
        else:
            url = botfunc.get_config('setu_api')
        print(f'使用URL：{url}（p={p}, ch={ch}, (ch == p)={ch == p}）')
        # 涩图不一样，这里不能使用缓存
        async with ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()
        botfunc.safe_file_write(filename=f'{index}.png', mode='wb', s=data)
    await subprocess.create_subprocess_shell(f"7z a {fdir}/res.7z {fdir} -p{group.id} ")
    await app.upload_file(data=botfunc.safe_file_read(f'{fdir}/res.7z', mode='rb'), target=group,
                          name=f"s{time.time()}.7z")
    await asyncio.sleep(botfunc.get_config('recall'))
    os.removedirs(fdir)
