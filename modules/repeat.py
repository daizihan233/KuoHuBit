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
from loguru import logger

import botfunc
from botfunc import r

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
    if group.id not in botfunc.get_dyn_config("mute") and message.as_persistent_string() != "<! 不支持的消息类型 !>":
        logger.debug(f"hexists {hash_name} {group.id}")
        if r.hexists(hash_name, f"{group.id}"):
            td = r.hget(hash_name, f"{group.id}")
            logger.debug(f"hget {hash_name} {group.id}")
            td = str(td)
            logger.debug(
                f"{message.as_persistent_string()} == {urllib.parse.unquote(td)[2:-1]} ? {message.as_persistent_string() == urllib.parse.unquote(td)[2:-1]}")
            if message.as_persistent_string() == urllib.parse.unquote(td)[2:-1]:
                m = await app.send_group_message(
                    group,
                    MessageChain(
                        urllib.parse.unquote(td)
                    )
                )
                s = botfunc.r.hget("repeat_source", f"{group.id}")
                botfunc.r.hset("repeat_source", s, m.source)
                botfunc.r.hset("repeat_source", source.id, m.source)
                logger.debug(f"hget repeat_source {group.id}")
                logger.debug(f"hset repeat_source {s} {m.source}")
                logger.debug(f"hset repeat_source {source.id} {m.source}")
            else:
                r.hset(
                    hash_name,
                    f"{group.id}",
                    f"{urllib.parse.quote(message.as_persistent_string())}",
                )
                botfunc.r.hset("repeat_source", f"{group.id}", source.id)
                logger.debug(f"hset {hash_name} {group.id} {urllib.parse.quote(message.as_persistent_string())}")
                logger.debug(f"hset repeat_source {group.id} {source.id}")
        else:
            r.hset(
                hash_name,
                f"{group.id}",
                f"{urllib.parse.quote(message.as_persistent_string())}",
            )
            botfunc.r.hset("repeat_source", f"{group.id}", source.id)
            logger.debug(f"hset {hash_name} {group.id} {urllib.parse.quote(message.as_persistent_string())}")
            logger.debug(f"hset repeat_source {group.id} {source.id}")


@channel.use(ListenerSchema(listening_events=[GroupRecallEvent]))
async def del_msg(app: Ariadne, group: Group, event: GroupRecallEvent):
    if botfunc.r.hexists("repeat_source", event.message_id):
        await app.recall_message(botfunc.r.hget("repeat_source", event.message_id), group)
        botfunc.r.hdel("repeat_source", event.message_id)
