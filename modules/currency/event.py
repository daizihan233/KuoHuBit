from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import MemberLeaveEventQuit, MemberJoinEvent, MemberLeaveEventKick
from graia.ariadne.model import Group, Member
from graia.ariadne.util.saya import listen
from graia.saya import Channel

channel = Channel.current()
channel.name("event")
channel.description("有些事总是不知不觉的……")
channel.author("HanTools")


@listen(MemberLeaveEventQuit)
@listen(MemberLeaveEventKick)
async def leave(app: Ariadne, group: Group, member: Member):
    await app.send_message(
        target=group,
        message=f'[退][{member.id} | {member.name}] 退群力（悲）'
    )


@listen(MemberJoinEvent)
async def leave(app: Ariadne, group: Group, member: Member):
    await app.send_message(
        target=group,
        message=f'[入][{member.id} | {member.name}] 入群力（喜）'
    )
