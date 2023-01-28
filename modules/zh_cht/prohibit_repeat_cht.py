#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import yaml
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel

from modules.zh_cn.prohibit_repeat import dyn_config

channel = Channel.current()
channel.name("防刷屏")
channel.description("人類可真無聊")
channel.author("HanTools")


@listen(GroupMessage)
@decorate(MatchContent("開啟本群防刷屏"))
async def start_mute(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    cfy['mute'].append(group.id)
    cfy['mute'] = list(set(cfy["mute"]))
    with open(dyn_config, 'w') as cf:
        yaml.dump(cfy, cf)
    await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK辣！")))


@listen(GroupMessage)
@decorate(MatchContent("關閉本群防刷屏"))
async def stop_mute(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    try:
        cfy['mute'].remove(group.id)
        cfy['mute'] = list(set(cfy["mute"]))
        with open(dyn_config, 'w') as cf:
            yaml.dump(cfy, cf)
        await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK辣！")))
    except Exception as err:
        await app.send_message(group, MessageChain(At(event.sender.id), Plain(f" 报错辣！{err}")))
