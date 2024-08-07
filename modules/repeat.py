#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import urllib.parse

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import GroupRecallEvent
from graia.ariadne.message import Source
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.channel import ChannelMeta

from utils.cache import r
from utils.config import get_dyn_config

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "复读"
channel.meta["description"] = "人类有时候还是挺有趣的其实（？）"
channel.meta["author"] = "KuoHu"

dyn_config = "dynamic_config.yaml"
hash_name = "bot_repeat"


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def repeat(
        app: Ariadne, group: Group, message: MessageChain, source: Source
):
    if group.id not in get_dyn_config("mute") and message.as_persistent_string() != "<! 不支持的消息类型 !>":
        if r.hexists(hash_name, f"{group.id}"):
            td = str(r.hget(hash_name, f"{group.id}"))[2:-1]
            tc = int(td.split(",")[0])
            td = str(td.split(",")[1])
            if message.as_persistent_string() == urllib.parse.unquote(td):
                if tc == 1:
                    m = await app.send_group_message(
                        group,
                        MessageChain.from_persistent_string(
                            urllib.parse.unquote(td)
                        )
                    )
                    s = r.hget("repeat_source", f"{group.id}")
                    r.hset("repeat_source", s, m.source.id)
                    r.hset("repeat_source", source.id, m.source.id)
                    r.hset(
                        hash_name,
                        f"{group.id}",
                        f"{tc + 1},{urllib.parse.quote(message.as_persistent_string())}",
                    )
            else:
                r.hset(
                    hash_name,
                    f"{group.id}",
                    f"1,{urllib.parse.quote(message.as_persistent_string())}",
                )
                r.hset("repeat_source", f"{group.id}", source.id)
        else:
            r.hset(
                hash_name,
                f"{group.id}",
                f"1,{urllib.parse.quote(message.as_persistent_string())}",
            )
            r.hset("repeat_source", f"{group.id}", source.id)


@channel.use(ListenerSchema(listening_events=[GroupRecallEvent]))
async def del_msg(app: Ariadne, group: Group, event: GroupRecallEvent):
    if r.hexists("repeat_source", event.message_id):
        await app.recall_message(r.hget("repeat_source", event.message_id), group)
        r.hdel("repeat_source", event.message_id)
