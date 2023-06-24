import random

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message import Source
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

import botfunc
import cache_var

channel = Channel.current()
channel.name("inm")
channel.description("哼哼哼，啊啊啊啊啊")
channel.author("HanTools")


@channel.use(SchedulerSchema(timers.crontabify("45 11 * * * 14")))
async def inm(app: Ariadne):
    for group in cache_var.inm:
        await app.send_group_message(
            target=group,
            message=f"哼哼哼，{'啊' * random.randint(5, 20)}"
        )


@listen(GroupMessage)
@decorate(MatchContent("臭死力"))
async def homo(app: Ariadne, group: Group, source: Source, event: GroupMessage):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    cache_var.inm.append(group.id)
    await botfunc.run_sql("INSERT INTO inm VALUES (%s)", (group.id,))
    await app.send_message(
        target=group,
        quote=source,
        message='草'
    )


@listen(GroupMessage)
@decorate(MatchContent("香死力"))
async def homo(app: Ariadne, group: Group, source: Source, event: GroupMessage):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    cache_var.inm.remove(group.id)
    await botfunc.run_sql("DELETE FROM inm WHERE gid=%s", (group.id,))
    await app.send_message(
        target=group,
        quote=source,
        message='艹'
    )
