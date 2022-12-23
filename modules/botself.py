#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.ariadne.event.mirai import NewFriendRequestEvent, BotInvitedJoinGroupRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("自身信息处理")
channel.description("简称自理")
channel.author("HanTools")


# 好友添加
@channel.use(
    ListenerSchema(
        listening_events=[NewFriendRequestEvent]
    )
)
async def new_friend(event: NewFriendRequestEvent):
    if botfunc.get_config('NewFriendRequestEvent'):
        await event.accept()
    else:
        await event.reject()


# 邀请加群
@channel.use(
    ListenerSchema(
        listening_events=[BotInvitedJoinGroupRequestEvent]
    )
)
async def new_friend(event: BotInvitedJoinGroupRequestEvent):
    if botfunc.get_config('BotInvitedJoinGroupRequestEvent'):
        await event.accept()
    else:
        await event.reject()
