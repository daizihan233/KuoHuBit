#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, TempMessage
from graia.ariadne.model import Member, Friend
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from graia.saya.channel import ChannelMeta

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "如来"
channel.meta["description"] = "在有人找机器人私聊的时候，如来"
channel.meta["author"] = "KuoHu"


rutext = """中国人认为宇宙万法的那个源头
它是什么
它是如如
对吧
所以这个词叫如来
我经常说如来 
这个词有秘密
如来，如来了吗？如来嘛！
他真来了吗，如来！
到底来没来？如来！
我问如来，他真来了吗？如来！
你看看，来没来？如来！
他很厉害，他不是一个有形的
所以你读《心经》，《心经》里面讲什么
观自在菩萨，般若波罗蜜多时，照见五蕴皆空注意，不生不灭，不垢不净，不增不减，如如不动
所以，万物生于有，有生于无，是这样说的吧
他不是个实体
我有一次去甘肃讲课，遇到一个人
他的老师，当时有七十多岁了
那个七十多岁的老人家
就问那个小伙子
他说真有佛吗？这个世界真有佛吗？
一下子把小伙子问傻了
有
他说真有吗
一下就问傻了
你想想那是个真理
真理是无相的
所以《金刚经》的一句话
叫凡有所相，皆是虚妄，见所相非相
那是个真理，你不能迷信，在这方面他是个真理
所以道可道，非常道，名可名，非常名
但是说那有人说，我非得说，你非得说
我可以告诉你
老子也没说明白
他不是语言可以描述的
后来西方的语言哲学家，叫维特根斯坦
把这个事说了一句名言
维特根斯坦说，这个世界上有语言能说的，叫说清楚，这个世界上也有超出语言，说不明白的，维特根斯坦直接用了俩字，闭嘴
那没法说嘛
所以才有了，如来什么，拈花，迦叶微笑""".split(
    "\n"
)

index = 0


async def send_ru(app: Ariadne, sender: Member or Friend):
    global index
    await app.send_message(sender, rutext[index])
    index += 1
    if index > len(rutext) - 1:
        index = 0


@listen(TempMessage)
async def rulai(app: Ariadne, sender: Member):
    await send_ru(app, sender)


@listen(FriendMessage)
async def rulai(app: Ariadne, sender: Friend):
    await send_ru(app, sender)
