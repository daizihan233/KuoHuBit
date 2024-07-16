#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import pymysql.err
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import MemberJoinEvent
from graia.ariadne.message.element import At
from graia.ariadne.message.parser.base import DetectPrefix
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta
from loguru import logger

from utils import depen
from utils.config import get_all_admin
from utils.sql import run_sql, select_fetchone

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "黑名单"
channel.meta["description"] = "屑"
channel.meta["author"] = "KuoHu"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            DetectPrefix("拉黑"),
            depen.check_authority_bot_op(),
            depen.check_authority_not_black(),
        ],
    )
)
async def nmsl(
        app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("拉黑")
):
    msg = "--- 执行结果 ---\n"
    flag = True
    for i in message[At]:
        flag = False
        msg += f"{i}：\n"
        try:
            await run_sql(
                "INSERT INTO blacklist(uid, op) VALUES (%s, %s)",
                (i.target, event.sender.id),
            )
        except Exception as err:
            logger.warning(f"{i} 未能成功加入数据库：{err}")
            msg += f"    数据库：【错误：{err}】\n"
        else:
            msg += "    数据库：成功\n"
        try:
            await app.kick_member(event.sender.group.id, event.sender.id)
        except PermissionError:
            logger.warning(f"{i} 未能成功踢出：权限错误")
            msg += "    踢出：【错误：无权踢出】"
        else:
            msg += "    踢出：成功"
        msg += "\n"
    if flag:
        try:
            await run_sql(
                "INSERT INTO blacklist(uid, op) VALUES (%s, %s)",
                (int(str(message)), event.sender.id),
            )
        except TypeError:
            await app.send_message(event.sender.group, "类型错误，无法添加至数据库")
            return
        except pymysql.err.IntegrityError:
            await app.send_message(event.sender.group, "此人已在数据库")
            return
        else:
            try:
                await app.kick_member(event.sender.group.id, event.sender.id)
            except PermissionError:
                await app.send_message(event.sender.group, "已成功添加进黑名单数据库，但机器人无权踢出此人")
            else:
                await app.send_message(event.sender.group, "已成功添加进黑名单数据库并踢出了此人")
    else:
        await app.send_message(event.sender.group, msg)


@channel.use(
    ListenerSchema(
        listening_events=[MemberJoinEvent],
        decorators=[depen.check_authority_black(False)],
    )
)
async def kicksb(app: Ariadne, event: MemberJoinEvent):
    admins = await get_all_admin()
    if event.inviter.id not in admins:
        t = await select_fetchone(
            "SELECT uid, op FROM blacklist WHERE uid = %s", (event.member.id,)
        )
        try:
            await app.kick_member(event.member.group)
        except PermissionError:
            await app.send_message(
                event.member.group,
                f"{event.member.id} 在机器人的黑名单列表中，由 {t[1]} 添加，但机器人权限过低，无法踢出",
            )
        else:
            await app.send_message(event.member.group, f"{event.member.id} 被踢出去辣！（喜）")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            DetectPrefix("删黑"),
            depen.check_authority_bot_op(),
            depen.check_authority_not_black(),
        ],
    )
)
async def nmms(
        app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("删黑")
):
    try:
        await run_sql(
            "DELETE FROM blacklist WHERE uid = %s", (int(str(message)),)
        )
        await app.send_message(event.sender.group, "好乐！")
    except Exception as err:
        await app.send_message(event.sender.group, f"Umm，{err}")
