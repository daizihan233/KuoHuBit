import asyncio
import os
import re
import time

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

sl1 = ["6", "9", "6的", "9（6翻了）", "⑥"]
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


async def divided(a, b):
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
async def get_all_words(lst_aa, lst_bb):
    all_word = []
    for ix in lst_aa:
        if ix not in all_word:
            all_word.append(ix)
    for j in lst_bb:
        if j not in all_word:
            all_word.append(j)
    return all_word


# 词频向量化
async def get_word_vector(lst_aaa, lst_bbb, all_word):
    la = []
    lb = []
    for word in all_word:
        la.append(lst_aaa.count(word))
        lb.append(lst_bbb.count(word))
    return la, lb


# 计算余弦值，利用了numpy中的线代计算方法
async def calculate_cos(la, lb):
    laaa = numpy.array(la)
    lbbb = numpy.array(lb)
    coss = (numpy.dot(laaa, lbbb.T)) / ((numpy.sqrt(numpy.dot(laaa, laaa.T))) * (numpy.sqrt(numpy.dot(lbbb, lbbb.T))))
    return float(coss)


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


async def f_hide_mid(string, count=4, fix='*'):
    """
       #隐藏/脱敏 中间几位
       str 字符串
       count 隐藏位数
       fix 替换符号
    """
    if not string:
        return ''
    count = int(count)
    str_len = len(string)
    if str_len == 1:
        return string
    elif str_len == 2:
        ret_str = string[0] + '*'
    elif count == 1:
        mid_pos = int(str_len / 2)
        ret_str = string[:mid_pos] + fix + string[mid_pos + 1:]
    else:
        if str_len - 2 > count:
            if count % 2 == 0:
                if str_len % 2 == 0:
                    ret_str = string[:int(str_len / 2 - count / 2)] + count * fix + string[
                                                                                    int(str_len / 2 + count / 2):]
                else:
                    ret_str = string[:int((str_len + 1) / 2 - count / 2)] + count * fix + string[int((
                                                                                                             str_len + 1) / 2 + count / 2):]
            else:
                if str_len % 2 == 0:
                    ret_str = string[:int(str_len / 2 - (count - 1) / 2)] + count * fix + string[int(str_len / 2 + (
                            count + 1) / 2):]
                else:
                    ret_str = string[:int((str_len + 1) / 2 - (count + 1) / 2)] + count * fix + string[
                                                                                                int((
                                                                                                            str_len + 1) / 2 + (
                                                                                                            count - 1) / 2):]
        else:
            ret_str = string[0] + fix * (str_len - 2) + string[-1]
    return ret_str


async def text_pretreatment(s):
    regex = re.compile(r"6+")
    regex2 = re.compile(r"9+")
    s = s.strip(" ，,。.!！？?()（）")
    s = regex.sub('6', s)
    s = regex2.sub('9', s)
    return s


async def index_lst(x, lst):
    lst = sorted(lst, reverse=True, key=lambda n: n[1])
    flag = len(lst) - 1
    for i in range(len(lst)):
        if x > lst[i][1]:
            flag = i
            break
    msg = []
    for i in range(flag):
        msg.append(f"{lst[i][0]} --> {lst[i][1]}")
    return msg, flag


async def vague(i: int):
    ret = list(str(i))
    return int(f'{ret[0]}{"0" * len(ret)}')


async def selectivity_hide(lst):
    avg = await vague(numpy.average([x[1] for x in lst]))
    msg, ind = await index_lst(avg, lst)
    for i in range(ind, min(len(lst), ind + 10)):
        aw = await f_hide_mid(str(lst[i][0]), len(str(lst[i][0])) // 2)
        msg.append(f"{aw} --> {lst[i][1]}")
    return msg


@listen(GroupMessage)
async def six_six_six(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain):
    data = await select_fetchone("""SELECT uid, count, ti, ban_ti FROM six WHERE uid = %s""", event.sender.id)
    if data is not None and int(time.time()) - data[3] < 10:
        return
    msg = [x.text for x in message.get(Plain)]
    for s1 in sl1:
        # 文本预处理
        s1_ = await text_pretreatment(s1)
        s2_ = await text_pretreatment("".join(msg))
        # 对比
        list_a, list_b = await divided(s1_, s2_)
        all_words = await get_all_words(tuple(list_a), tuple(list_b))
        laa, lbb = await get_word_vector(tuple(list_a), tuple(list_b), tuple(all_words))
        cos = await calculate_cos(tuple(laa), tuple(lbb))
        cos = round(cos, 2)
        # 判断
        if cos >= 0.75:  # 判断为 6
            if data is not None:
                await else_sql("""UPDATE six SET count = count + 1 WHERE uid = %s""", (event.sender.id,))
            else:
                await else_sql("""INSERT INTO six VALUES (%s, 1, %s, 0)""", (event.sender.id, int(time.time())))
            if data is None or time.time() - data[2] >= 600:
                await app.send_group_message(target=group,
                                             message=MessageChain(
                                                 [At(event.sender.id),
                                                  Image(path=os.path.abspath(
                                                      os.curdir) + '/img/6.jpg')]),
                                             quote=event.source)
                await else_sql("""UPDATE six SET ti = %s, ban_ti=unix_timestamp() WHERE uid = %s""",
                               (int(time.time()), event.sender.id))

            break


@listen(GroupMessage)
@decorate(MatchContent("6榜"))
async def six_six_six(app: Ariadne, group: Group):
    data = await select_fetchall("SELECT uid, count FROM six ORDER BY count DESC")
    msg = await selectivity_hide(data)
    await app.send_group_message(group, Plain("\n".join(msg)))
