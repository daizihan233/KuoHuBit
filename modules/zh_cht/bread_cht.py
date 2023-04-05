#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import math
import random
import time

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import DetectPrefix, MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

import botfunc
from modules.zh_cn.bread import get_data_sql

channel = Channel.current()
channel.name("麵包廠")
channel.description("好吃")
channel.author("HanTools")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def get_bread(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain = DetectPrefix("來份麵包")):
    data = message.display
    data = data.lstrip(' ')
    data = data.rstrip(' ')
    if not data:
        data = 1
    try:
        data = int(data)
    except Exception as err:
        await app.send_message(group, MessageChain([At(event.sender.id), Plain(f" 報錯啦……{err}")]))
    else:
        result = await botfunc.select_fetchone(get_data_sql, (group.id,))

        res = list(result)
        res[3] += ((int(time.time()) - res[2]) // 60) * random.randint(0, math.ceil((2 ** res[1] - res[3]) * 0.08))
        res[2] = int(time.time())
        # 如果面包仓库爆满则强制使其等于上限
        if res[3] > 2 ** result[1]:
            res[3] = 2 ** result[1]
        # 如果够
        if res[3] - data >= 0:
            res[3] -= data
            await app.send_message(group, MessageChain(
                [At(event.sender.id), Plain(f" {'🍞' * data if data < 50 else '🍞*' + str(data)}")]))
        else:  # 如果不够
            await app.send_message(group, MessageChain(
                [At(event.sender.id), Plain(f" 麵包不夠喲~ 現在只有 {res[3]} 塊麵包！")]))
        sql_2 = '''UPDATE bread SET time = %s, bread = %s WHERE id = %s'''
        await botfunc.run_sql(sql_2, (res[2], res[3], group.id))


@listen(GroupMessage)
@decorate(MatchContent("麵包廠信息"))
async def setu(app: Ariadne, group: Group):
    result = await botfunc.select_fetchone(get_data_sql, (group.id,))

    res = list(result)
    res[3] = ((int(time.time()) - res[2]) // 60) * random.randint(0, math.ceil((2 ** res[1] - res[3]) * 0.08)) + res[3]
    if res[3] > 2 ** result[1]:
        res[3] = 2 ** result[1]
    res[2] = int(time.time())
    sql_2 = '''UPDATE bread SET time = %s, bread = %s WHERE id = %s'''
    await botfunc.run_sql(sql_2, (res[2], res[3], group.id))
    try:
        await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）麵包廠信息如下：\n'
                                                          f'等級：{result[1]} 級\n'
                                                          f'經驗值：{result[4]} / {2 ** result[1]}\n'
                                                          f'現有麵包：{res[3]} / {2 ** result[1]}')]))
    except ValueError:
        logger.warning('【1】为防止 DoS 攻击程序禁止了int -> str的强制类型转换')
        try:
            await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）麵包廠信息如下：\n'
                                                              f'等級：{result[1]} 級\n'
                                                              f'經驗值：{result[4]} / 很大\n'
                                                              f'現有麵包：{res[3]} / 很大')]))
        except ValueError:
            logger.warning('【2】为防止 DoS 攻击程序禁止了int -> str的强制类型转换')
            await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）麵包廠信息\n'
                                                              f'等級：{result[1]} 級\n'
                                                              f'經驗值：很大 / 很大\n'
                                                              f'現有麵包：很大 / 很大')]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectPrefix("來份炒飯")]
    )
)
async def get_bread(app: Ariadne, group: Group, event: GroupMessage):
    await app.send_group_message(group, "啊？", quote=event.source)
