#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, ActiveGroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent
from graia.ariadne.message import Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.channel import ChannelMeta

from utils.cache import r

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "Hello World!"
channel.meta["description"] = "哼哼哼，啊啊啊啊啊"
channel.meta["author"] = "KuoHu"


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def echo(
        app: Ariadne,
        group: Group,
        source: Source,
        message: MessageChain = DetectPrefix("/echo "),
):
    for w in ("echo", "6", "9"):
        if message.display.startswith(w):
            return
    m: ActiveGroupMessage = await app.send_group_message(
        group,
        message,
    )
    r.hset("echo", source.id, m.source.id)


@channel.use(ListenerSchema(listening_events=[GroupRecallEvent]))
async def echo(app: Ariadne, group: Group, event: GroupRecallEvent):
    if r.hexists("echo", event.message_id):
        await app.recall_message(r.hget("echo", event.message_id), group)
        r.hdel("echo", event.message_id)
