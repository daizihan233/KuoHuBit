import asyncio

import aiomysql
import jieba
import opencc
import yaml
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent, DetectPrefix
from graia.ariadne.model import Group, MemberPerm
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from loguru import logger

import botfunc
import cache_var

channel = Channel.current()
channel.name("敏感词检测")
channel.description("防止群被炸")
channel.author("HanTools")
opc = opencc.OpenCC('t2s')
dyn_config = 'dynamic_config.yaml'
loop = asyncio.get_event_loop()
jieba.load_userdict("./jieba_words.txt")


async def run_sql(sql, arg):
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


@listen(GroupMessage)
@decorate(MatchContent("開啟本群敏感詞檢測"))
async def start_word(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    cfy['word'].append(group.id)
    cfy['word'] = list(set(cfy["word"]))
    with open(dyn_config, 'w') as cf:
        yaml.dump(cfy, cf)
    await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK啦！")))


@listen(GroupMessage)
@decorate(MatchContent("關閉本群敏感詞檢測"))
async def stop_word(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    try:
        cfy['word'].remove(group.id)
        cfy['word'] = list(set(cfy["word"]))
        with open(dyn_config, 'w') as cf:
            yaml.dump(cfy, cf)
        await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK啦！")))
    except Exception as err:
        await app.send_message(group, MessageChain(At(event.sender.id), Plain(f" 報錯啦！{err}")))


@listen(GroupMessage)
async def add(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("加敏感詞")):
    if event.sender.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        if str(message) not in cache_var.sensitive_words:
            try:
                await run_sql('INSERT INTO wd(wd) VALUES (%s)', (message,))
            except Exception as err:
                await app.send_message(event.sender.group, f'寄！{err}')
            else:
                await app.send_message(event.sender.group, f'好啦！')
            try:
                cache_var.sensitive_words.append(str(message))
            except Exception as err:
                logger.error(err)
        else:
            await app.send_message(event.sender.group, f'有沒有一種可能，這個詞已經加過了')


@listen(GroupMessage)
async def rm(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("刪敏感詞")):
    if event.sender.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        try:
            await run_sql('DELETE FROM wd WHERE wd=%s', (message,))
        except Exception as err:
            await app.send_message(event.sender.group, f'寄！{err}')
        else:
            await app.send_message(event.sender.group, f'好啦！')
        try:
            cache_var.sensitive_words.remove(str(message))
        except Exception as err:
            logger.error(err)
