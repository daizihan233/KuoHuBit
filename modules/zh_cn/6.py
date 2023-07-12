import os
import random
import re
import time

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
import cache_var

channel = Channel.current()
channel.name("6榜")
channel.description("666")
channel.author("HanTools")

sl1 = ["6", "9", "6的", "9（6翻了）", "⑥", "₆", "⑹", "⒍", "⁶", "six", "nine", "\u0039\ufe0f\u20e3",
       "\u0036\ufe0f\u20e3", "♸", "𝟼", "𝟞", "liù", "liu"]  # 模糊匹配
sl2 = []  # 精确匹配
jieba.load_userdict('./jieba_words.txt')


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
    s = s.replace('六', '6').replace('九', '9').replace('陆', '6').replace('玖', '9') \
        .replace('(', '（').replace(')', '）').lower()
    stop_words = " ，,。.!！？?…^\n"
    for stop in stop_words:
        s = s.replace(stop, '')
    replace_words = [
        "（", "）"
    ]
    for regex in sl1 + sl2 + replace_words:
        s = re.compile(f"({regex})+").sub(regex, s)
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


async def selectivity_hide(lst):
    avg = int(numpy.average([x[1] for x in lst]))
    msg, ind = await index_lst(avg, lst)
    for i in range(ind, min(len(lst), ind + 10)):
        aw = await f_hide_mid(str(lst[i][0]), len(str(lst[i][0])) // 2)
        msg.append(f"{aw} --> {lst[i][1]}")
    return msg


@listen(GroupMessage)
async def six_six_six(app: Ariadne, group: Group, event: GroupMessage, message: MessageChain):
    data = await botfunc.select_fetchone("""SELECT uid, count, ti FROM six WHERE uid = %s""", event.sender.id)
    if data is not None and int(time.time()) - data[2] < 10:
        await botfunc.run_sql("""UPDATE six SET ti = unix_timestamp() WHERE uid = %s""", (event.sender.id,))
        return
    msg = [x.text for x in message.get(Plain)]
    s2_ = await text_pretreatment("".join(msg))
    if s2_ in sl2:
        if data is not None:
            await botfunc.run_sql("""UPDATE six SET count = count+1, ti = unix_timestamp() WHERE uid = %s""",
                                  (event.sender.id,))
        else:
            await botfunc.run_sql("""INSERT INTO six VALUES (%s, 1, unix_timestamp())""", (event.sender.id,))
        if data is None or time.time() - data[2] >= 600:
            img = os.listdir(os.path.abspath(os.curdir) + '/img/6/')
            await app.send_group_message(target=group,
                                         message=MessageChain(
                                             [At(event.sender.id),
                                              Image(path=os.path.abspath(os.curdir) + '/img/6/' + random.choice(
                                                  img))]),
                                         quote=event.source)
        return
    for s1 in sl1:
        # 文本预处理
        s1_ = await text_pretreatment(s1)
        # 对比
        list_a, list_b = await divided(s1_, s2_)
        all_words = await get_all_words(tuple(list_a), tuple(list_b))
        laa, lbb = await get_word_vector(tuple(list_a), tuple(list_b), tuple(all_words))
        cos = await calculate_cos(tuple(laa), tuple(lbb))
        cos = round(cos, 2)
        # 判断
        if cos >= 0.75:  # 判断为 6
            if data is not None:
                await botfunc.run_sql("""UPDATE six SET count = count+1, ti = unix_timestamp() WHERE uid = %s""",
                                      (event.sender.id,))
            else:
                await botfunc.run_sql("""INSERT INTO six VALUES (%s, 1, unix_timestamp())""", (event.sender.id,))
            if group.id not in cache_var.no_6 and (data is None or time.time() - data[2] >= 600):
                img = os.listdir(os.path.abspath(os.curdir) + '/img/6/')
                await app.send_group_message(target=group,
                                             message=MessageChain(
                                                 [At(event.sender.id),
                                                  Image(path=os.path.abspath(os.curdir) + '/img/6/' + random.choice(
                                                      img))]),
                                             quote=event.source)
            break


@listen(GroupMessage)
@decorate(MatchContent("6榜"))
async def six_top(app: Ariadne, group: Group, event: GroupMessage):
    data = await botfunc.select_fetchall("SELECT uid, count FROM six ORDER BY count DESC LIMIT 21")
    try:
        msg = await selectivity_hide(data)
    except ValueError:
        await app.send_group_message(group, MessageChain([At(event.sender.id), Plain(" 木有数据~")]),
                                     quote=event.source)
    else:
        await app.send_group_message(group, MessageChain([At(event.sender.id), Plain(" \n"), Plain("\n".join(msg))]),
                                     quote=event.source)


@listen(GroupMessage)
@decorate(MatchContent("6，闭嘴"))
async def no_six(app: Ariadne, group: Group, event: GroupMessage):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    if group.id not in cache_var.no_6:
        cache_var.no_6.append(group.id)
        await botfunc.run_sql("""INSERT INTO no_six VALUES (%s)""", (group.id,))
        await app.send_group_message(
            group,
            MessageChain(
                [
                    At(event.sender.id),
                    Plain(" 好啊，很好啊")
                ]
            ),
            quote=event.source
        )


@listen(GroupMessage)
@decorate(MatchContent("6，张嘴"))
async def yes_six(app: Ariadne, group: Group, event: GroupMessage):
    admins = await botfunc.get_all_admin()
    if event.sender.id not in admins:
        return
    if group.id in cache_var.no_6:
        cache_var.no_6.remove(group.id)
        await botfunc.run_sql("""DELETE FROM no_six WHERE gid = %s""", (group.id,))
        await app.send_group_message(
            group,
            MessageChain(
                [
                    At(event.sender.id),
                    Plain(" 好啊，很好啊")
                ]
            ),
            quote=event.source
        )
