#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import random

import loguru
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message import Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

from utils import depen, var
from utils.data import get_all_admin
from utils.sql import run_sql

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "inm"
channel.meta["description"] = "哼哼哼，啊啊啊啊啊"
channel.meta["author"] = "KuoHu"


@channel.use(SchedulerSchema(timers.crontabify("45 11 * * * 14")))
async def inm(app: Ariadne):
    for group in var.inm:
        try:
            await app.send_group_message(
                target=group, message=f"哼哼哼，{'啊' * random.randint(5, 20)}"
            )
        except ValueError:
            loguru.logger.warning(
                f"{group} 不存在！请检查机器人是否被踢出，请尝试让机器人重新加群或手动删除数据库数据并重启机器人！"
            )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("臭死力"), depen.check_authority_op()],
    )
)
async def homo(app: Ariadne, group: Group, source: Source):
    if group.id in var.inm:
        return
    var.inm.append(group.id)
    await run_sql("INSERT INTO inm VALUES (%s)", (group.id,))
    await app.send_message(target=group, quote=source, message="草")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("香死力"), depen.check_authority_op()],
    )
)
async def homo(app: Ariadne, group: Group, source: Source, event: GroupMessage):
    admins = await get_all_admin()
    if event.sender.id not in admins:
        return
    if group.id not in var.inm:
        return
    var.inm.remove(group.id)
    await run_sql("DELETE FROM inm WHERE gid=%s", (group.id,))
    await app.send_message(target=group, quote=source, message="艹")
