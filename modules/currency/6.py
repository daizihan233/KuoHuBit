import asyncio
import math
import os
import re

import aiomysql
import jieba
import numpy
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel

import botfunc

channel = Channel.current()
channel.name("6榜")
channel.description("666")
channel.author("HanTools")
loop = asyncio.get_event_loop()

sl1 = ["6", "9", "6的", "9（6翻了）"]
jieba.load_userdict('./jieba_words.txt')


async def select_fetchall(sql, arg=None):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return r


def divided(a, b):
    a1 = jieba.cut(a)
    b1 = jieba.cut(b)
    lst_a = []
    lst_b = []
    for i in a1:
        lst_a.append(i)
    for j in b1:
        lst_b.append(j)
    return lst_a, lst_b


# 获取所有的分词可能
def get_all_words(lst_aa, lst_bb):
    all_word = []
    for ix in lst_aa:
        if ix not in all_word:
            all_word.append(ix)
    for j in lst_bb:
        if j not in all_word:
            all_word.append(j)
    return all_word


# 词频向量化
def get_word_vector(lst_aaa, lst_bbb, all_word):
    la = []
    lb = []
    for word in all_word:
        la.append(lst_aaa.count(word))
        lb.append(lst_bbb.count(word))
    return la, lb


# 计算余弦值，利用了numpy中的线代计算方法
def calculate_cos(la, lb):
    laaa = numpy.array(la)
    lbbb = numpy.array(lb)
    coss = (numpy.dot(laaa, lbbb.T)) / ((math.sqrt(numpy.dot(laaa, laaa.T))) * (math.sqrt(numpy.dot(lbbb, lbbb.T))))
    return coss


async def else_sql(sql, arg):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    await cur.execute(sql, arg)
    await cur.execute("commit")
    await cur.close()
    conn.close()


async def select_fetchone(sql, arg=None):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    r = await cur.fetchone()
    await cur.close()
    conn.close()
    return r


@listen(GroupMessage)
async def six_six_six(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain):
    data = await select_fetchone("""SELECT uid, count FROM six WHERE uid = %s""", event.sender.id)
    msg = [x.text for x in message.get(Plain)]
    for s1 in sl1:
        # 文本预处理
        s1_ = s1.strip(" ，,。.!！？?()（）")
        s2_ = msg.strip(" ，,。.!！？?()（）")
        regex = re.compile(r"6+")
        regex2 = re.compile(r"9+")
        s1_ = regex.sub('6', s1_)
        s2_ = regex.sub('6', s2_)
        s1_ = regex2.sub('9', s1_)
        s2_ = regex2.sub('9', s2_)
        # 对比
        list_a, list_b = divided(s1_, s2_)
        all_words = get_all_words(list_a, list_b)
        laa, lbb = get_word_vector(list_a, list_b, all_words)
        cos = calculate_cos(laa, lbb)
        cos = round(cos, 2)
        # 判断
        if cos >= 0.75:  # 判断为 6
            if data is not None:
                await else_sql("""UPDATE six SET count = count + 1 WHERE uid = %s""", (event.sender.id,))
            else:
                await else_sql("""INSERT INTO six VALUES (%s, 1)""", (event.sender.id,))
            await app.send_group_message(target=group,
                                         message=MessageChain([At(event.sender.id),
                                                               Image(path=os.path.abspath(os.curdir) + '/img/6.jpg')]),
                                         quote=event.source)
            break


@listen(GroupMessage)
@decorate(MatchContent("6榜"))
async def six_six_six(app: Ariadne, group: Group):
    data = await select_fetchall("SELECT uid, count FROM six ORDER BY count DESC LIMIT 10")
    msg = []
    for i in data:
        msg.append(f"{i[0]} --> {i[1]} 次")
        await app.send_group_message(group, Plain("\n".join(msg)))
