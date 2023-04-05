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

channel = Channel.current()
channel.name("面包厂")
channel.description("好吃")
channel.author("HanTools")
get_data_sql = '''SELECT id, level, time, bread, experience FROM bread WHERE id = %s'''


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def get_bread(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain = DetectPrefix("来份面包")):
    data = message.display
    data = data.lstrip(' ')
    data = data.rstrip(' ')
    if not data:
        data = 1
    try:
        data = int(data)
    except Exception as err:
        await app.send_message(group, MessageChain([At(event.sender.id), Plain(f" 报错啦……{err}")]))
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
                [At(event.sender.id), Plain(f" 面包不够哟~ 现在只有 {res[3]} 块面包！")]))
        sql_2 = '''UPDATE bread SET time = %s, bread = %s WHERE id = %s'''
        await botfunc.run_sql(sql_2, (res[2], res[3], group.id))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def update_bread(group: Group):
    result = await botfunc.select_fetchone(get_data_sql, (group.id,))

    if result:
        res = list(result)
        res[4] += 1
        if res[4] >= (2 ** res[1]):
            res[1] += 1
            res[4] = 0
            sql = '''UPDATE bread SET level = %s, experience = %s WHERE id = %s'''
            await botfunc.run_sql(sql, (res[1], res[4], group.id))
        else:
            sql = '''UPDATE bread SET experience = %s WHERE id = %s'''
            await botfunc.run_sql(sql, (res[4], group.id))
    else:
        sql = '''INSERT INTO bread(id, level, time, bread, experience) VALUES (%s, 1, %s, 0, 0)'''
        await botfunc.run_sql(sql, (group.id, int(time.time())))


@listen(GroupMessage)
@decorate(MatchContent("面包厂信息"))
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
        await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）面包厂信息如下：\n'
                                                          f'等级：{result[1]} 级\n'
                                                          f'经验值：{result[4]} / {2 ** result[1]}\n'
                                                          f'现有面包：{res[3]} / {2 ** result[1]}')]))
    except ValueError:
        logger.warning('【1】为防止 DoS 攻击程序禁止了int -> str的强制类型转换')
        try:
            await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）面包厂信息如下：\n'
                                                              f'等级：{result[1]} 级\n'
                                                              f'经验值：{result[4]} / 很大\n'
                                                              f'现有面包：{res[3]} / 很大')]))
        except ValueError:
            logger.warning('【2】为防止 DoS 攻击程序禁止了int -> str的强制类型转换')
            await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）面包厂信息如下：\n'
                                                              f'等级：{result[1]} 级\n'
                                                              f'经验值：很大 / 很大\n'
                                                              f'现有面包：很大 / 很大')]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[DetectPrefix("来份炒饭")]
    )
)
async def get_bread(app: Ariadne, group: Group, event: GroupMessage):
    await app.send_group_message(group, "啊？", quote=event.source)
