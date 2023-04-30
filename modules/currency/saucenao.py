import datetime

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, Image, Forward, ForwardNode
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from loguru import logger

import botfunc

channel = Channel.current()
channel.name("snao搜图")
channel.description("工口发生！")
channel.author("HanTools")


@listen(GroupMessage)
@decorate(DetectPrefix("搜图"))
async def saucenao(app: Ariadne, group: Group, message: MessageChain, event: GroupMessage):
    if Image not in message:
        return
    image_results = botfunc.session.get('https://saucenao.com/search.php', params={
        "api_key": botfunc.get_cloud_config('snao_key'),
        "db": 999,  # 搜索所有数据库
        "output_type": 2,  # 以 Json 格式返回
        "testmode": 1,
        "numres": 16,
        "url": message[Image][0].url
    })
    image_results = image_results.json()['results']
    fwd_node_list = [
        ForwardNode(
            target=botfunc.get_config('qq'),  # 机器人QQ号
            time=datetime.datetime.now(),
            message=MessageChain([
                Plain(
                    "数据来源：https://saucenao.com/\n"
                    "没搜有到你想要的图片、搜出 r18 内容、你打开时被某张图片吓到等场景，我不负责"
                )
            ]),
            name="宇宙免责声明"
        )
    ]
    if not image_results:
        await app.send_group_message(group, MessageChain(Plain("没搜到！qwq")), quote=event.source)
        return
    await app.send_group_message(group, "让图片飞一会儿……", quote=event.source)
    for node in image_results[:min(len(image_results), 10)]:
        if not node['data'].get("ext_urls", None):
            continue
        node_url = '\n'.join(node['data']['ext_urls'])
        fwd_node_list.append(
            ForwardNode(
                target=botfunc.get_config('qq'),  # 机器人QQ号
                time=datetime.datetime.now(),
                message=MessageChain([
                    Plain(f"{node['header']['index_name']}\n"
                          f"相似度：{node['header']['similarity']}\n"),
                    Image(url=node['header']['thumbnail']),
                    Plain(f"\n{node_url}")
                ]),
                name="机器人"
            )
        )
    logger.debug(fwd_node_list)
    msg = MessageChain(
        Forward(
            fwd_node_list
        )
    )
    await app.send_message(group, msg)
