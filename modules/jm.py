# 本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import asyncio
import os
import pathlib
import shutil
import uuid

import jmcomic
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from graia.saya.channel import ChannelMeta
from graiax.shortcut.text_parser import DetectPrefix

from utils.file import safe_file_read

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "JM to PDF"
channel.meta["description"] = "掌握了核心科技"
channel.meta["author"] = "KuoHu"

jm_options = jmcomic.JmOption.default()
jm_options.download['image']['suffix'] = '.pdf'
jm_options.dir_rule.base_dir = './work/jm/'
jm_options.dir_rule['rule'] = 'Aid'


async def download_comic(ids: list[str | int]):
    jm_options.download_album(ids)


@listen(GroupMessage)
async def setu_7z(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("jm ")):
    jmids = list(message.split(" "))
    uid = uuid.uuid4()
    fdir = f"./work/jm/{uuid}"
    pathlib.Path(fdir).mkdir(parents=True, exist_ok=True)
    await app.send_message(group, f"[{uid}] {'、'.join(jmids)} 正在下载中...")
    await download_comic(jmids)
    paths = [
        f'./work/jm/{x}.pdm' for x in jmids
    ]
    os.system(f"7z a {fdir}/res.7z {' '.join(paths)} -p{group.id}")
    await app.send_message(group, f"[{uuid}] 发射中……")
    await app.upload_file(
        data=safe_file_read(f"{fdir}/res.7z", mode="rb"),
        target=group,
        name=f"{uuid}.7z",
    )
    await asyncio.sleep(600)
    shutil.rmtree(fdir)
