import random

import loguru
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
import depen

channel = Channel.current()
channel.name("inm")
channel.description("哼哼哼，啊啊啊啊啊")
channel.author("HanTools")


@channel.use(SchedulerSchema(timers.crontabify("45 11 * * * 14")))
async def inm(app: Ariadne):
    for group in cache_var.inm:
        try:
            await app.send_group_message(
                target=group,
                message=f"哼哼哼，{'啊' * random.randint(5, 20)}"
            )
        except ValueError:
            loguru.logger.warning(
                f'{group} 不存在！请检查机器人是否被踢出，请尝试让机器人重新加群或手动删除数据库数据并重启机器人！')


@listen(GroupMessage)
@decorate(MatchContent("臭死力"))
@decorate(depen.check_authority_bot_op())
async def homo(app: Ariadne, group: Group, source: Source):
    if group.id in cache_var.inm:
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
@decorate(depen.check_authority_bot_op())
async def homo(app: Ariadne, group: Group, source: Source):
    if group.id not in cache_var.inm:
        return
    cache_var.inm.remove(group.id)
    await botfunc.run_sql("DELETE FROM inm WHERE gid=%s", (group.id,))
    await app.send_message(
        target=group,
        quote=source,
        message='艹'
    )
