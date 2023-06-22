import datetime

from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import MemberLeaveEventQuit, MemberJoinEvent, MemberLeaveEventKick
from graia.ariadne.message.element import Plain, At
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
        message=f'✈️成员发生变更：\n'
                f'QQ号为： {member.id} 的小伙伴退出了本群，对他/她的离开表示惋惜，期待他/她能够与我们再次相遇~'
    )


@listen(MemberJoinEvent)
async def leave(app: Ariadne, group: Group, member: Member):
    now = datetime.datetime.now()
    await app.send_message(
        target=group,
        message=MessageChain(
            [
                Plain('😘热烈欢迎 '),
                At(member.id),
                Plain(
                    f' 加入本群，入群时间为'
                    f'[{now.year}年{now.month}月{now.day}日 {now.hour}:{now.minute}:{now.second}]'
                    f'我是本群机器人（）,快来与群友们来互动吧~')
            ]
        )
    )
