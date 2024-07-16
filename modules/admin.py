#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta

from utils import depen
from utils.config import get_all_admin
from utils.sql import run_sql

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "管理员"
channel.meta["description"] = "对群和机器人进行管理"
channel.meta["author"] = "KuoHu"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            DetectPrefix("上管"),
            depen.check_authority_op(),
            depen.check_authority_not_black(),
        ],
    )
)
async def add_admin(
        app: Ariadne, group: Group, message: MessageChain = DetectPrefix("上管")
):
    try:
        await run_sql(
            "INSERT INTO admin(uid) VALUES (%s)", (int(str(message).lstrip("上管")),)
        )
    except Exception as err:
        await app.send_message(group, f"寄！{err}")
    else:
        await app.send_message(group, "OK!")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            DetectPrefix("下管"),
            depen.check_authority_op(),
            depen.check_authority_not_black(),
        ],
    )
)
async def del_admin(
        app: Ariadne,
        group: Group,
        event: GroupMessage,
        message: MessageChain = DetectPrefix("下管"),
):
    admins = await get_all_admin()
    if event.sender.id not in admins:
        return
    try:
        await run_sql("DELETE FROM admin WHERE uid = %s", (int(str(message)),))
    except Exception as err:
        await app.send_message(group, f"寄！{err}")
    else:
        await app.send_message(group, "OK!")
