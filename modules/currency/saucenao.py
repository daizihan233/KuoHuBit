#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import datetime

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, ForwardNode, Plain, Forward
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel

import botfunc

channel = Channel.current()
channel.name("snao搜图")
channel.description("工口发生！")
channel.author("HanTools")


@listen(GroupMessage)
@decorate(DetectPrefix("snao搜图"))
async def saucenao(app: Ariadne, group: Group, message: MessageChain, event: GroupMessage):
    if Image not in message:
        return
    image_results = botfunc.session.get('https://saucenao.com/search.php', params={
        "db": 999,  # 搜索所有数据库
        "output_type": 2,  # 以 Json 格式返回
        "testmode": 1,
        "numres": 16,
        "url": message[Image][0].url
    }).json()['results']
    fwd_node_list = []
    if not image_results:
        await app.send_group_message(group, MessageChain(Plain("没搜到！qwq")), quote=event.source)
        return
    for node in image_results[:min(len(image_results), 10)]:
        if not node['data']['ext_urls']:
            continue
        node_url = '\n'.join(node['data']['ext_urls'])
        fwd_node_list.append(
            ForwardNode(
                target=botfunc.get_config('qq'),
                time=datetime.datetime.now(),
                message=MessageChain([
                    Plain(f"{node['header']['index_name']}\n"
                          f"相似度：{node['header']['similarity']}\n"),
                    Image(url=node['header']['thumbnail']),
                    Plain(f"\n{node_url}")
                ])
            )
        )
    await app.send_group_message(
        group,
        MessageChain(
            Forward(
                fwd_node_list
            )
        )
    )
