from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.chain import MessageChain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("Nudge")
channel.description("你戳你妈呢？")
channel.author("HanTools")


@channel.use(ListenerSchema(listening_events=[NudgeEvent]))
async def getup(app: Ariadne, event: NudgeEvent):
    if event.target == botfunc.get_config('qq'):
        if event.context_type == "group":
            await app.send_group_message(
                event.group_id,
                MessageChain("你在戳什么？！")
            )
        elif event.context_type == "friend":
            await app.send_friend_message(
                event.friend_id,
                MessageChain("别戳我，好痒！")
            )
        else:
            return
