#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import random
import time
from functools import lru_cache

import pymysql
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import DetectPrefix, MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("来份涩图")
channel.description("人类有三大欲望……")
channel.author("HanTools")
conn = pymysql.connect(host='localhost', port=botfunc.get_cloud_config('MySQL_Port'), user='root',
                       password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                       database='Bot_bread')
cursor = conn.cursor()


@lru_cache()
def get_e(level: int):
    if level == 1:
        return 2
    return 2 ** get_e(level - 1)


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
        sql = f'''SELECT * FROM bread WHERE id = {group.id}'''
        cursor.execute(sql)
        result = cursor.fetchone()
        res = list(result)
        res[3] = ((int(time.time()) - res[2]) // 120) * random.randint(1, 5)
        res[2] = int(time.time())
        if res[3] - data >= 0:
            res[3] -= data
            await app.send_message(group, MessageChain(
                [At(event.sender.id), Plain(f" {'🍞' * data if data < 50 else '🍞*' + str(data)}")]))
        else:
            await app.send_message(group, MessageChain(
                [At(event.sender.id), Plain(f" 面包不够哟~ 现在只有 {res[3]} 块面包！")]))
        sql_2 = f'''UPDATE bread SET time = {res[2]}, bread = {res[3]} WHERE id = {group.id}'''
        cursor.execute(sql_2)
        conn.commit()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def update_bread(group: Group):
    sql = f'''SELECT * FROM bread WHERE id = {group.id}'''
    cursor.execute(sql)
    result = cursor.fetchone()
    if result:
        res = list(result)
        res[4] += 1
        if res[4] >= (2 ** res[1]):
            res[1] += 1
            res[4] = 0
            sql = f'''UPDATE bread SET level = {res[1]}, experience={res[4]} WHERE id = {group.id}'''
            cursor.execute(sql)
            conn.commit()
        else:
            sql = f'''UPDATE bread SET experience={res[4]} WHERE id = {group.id}'''
            cursor.execute(sql)
            conn.commit()
    else:
        sql = f'''INSERT INTO bread(id, level, time, bread, experience) VALUES ({group.id}, 1, {int(time.time())}, 0, 0)'''
        cursor.execute(sql)
        conn.commit()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("面包厂信息")],
    )
)
async def setu(app: Ariadne, group: Group):
    sql = f'''SELECT * FROM bread WHERE id = {group.id}'''
    cursor.execute(sql)
    result = cursor.fetchone()
    res = list(result)
    res[3] = ((int(time.time()) - res[2]) // 120) * random.randint(1, 5)
    if res[3] > 2 ** result[1]:
        res[3] = 2 ** result[1]
    res[2] = int(time.time())
    sql_2 = f'''UPDATE bread SET time = {res[2]}, bread = {res[3]} WHERE id = {group.id}'''
    cursor.execute(sql_2)
    conn.commit()
    try:
        await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）面包厂信息如下：\n'
                                                          f'等级：{result[1]} 级\n'
                                                          f'经验值：{result[4]} / {2 ** result[1]}\n'
                                                          f'现有面包：{res[3]} / {2 ** result[1]}')]))
    except ValueError:
        await app.send_message(group, MessageChain([Plain(f'本群（{result[0]}）面包厂信息如下：\n'
                                                          f'等级：{result[1]} 级\n'
                                                          f'经验值：{result[4]} / 很大\n'
                                                          f'现有面包：{res[3]} / 很大')]))
