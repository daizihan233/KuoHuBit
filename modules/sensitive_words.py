import asyncio

import aiomysql
import jieba
import opencc
import yaml
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent, DetectPrefix
from graia.ariadne.model import Group, Member
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc
import cache_var

channel = Channel.current()
channel.name("敏感词检测")
channel.description("防止群被炸")
channel.author("HanTools")
opc = opencc.OpenCC('t2s')
dyn_config = 'dynamic_config.yaml'
loop = asyncio.get_event_loop()


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
@decorate(MatchContent("开启本群敏感词检测"))
async def start_word(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    cfy['word'].append(group.id)
    cfy['word'] = list(set(cfy["word"]))
    with open(dyn_config, 'w') as cf:
        yaml.dump(cfy, cf)
    await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK辣！")))


@listen(GroupMessage)
@decorate(MatchContent("关闭本群敏感词检测"))
async def stop_word(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    try:
        cfy['word'].remove(group.id)
        cfy['word'] = list(set(cfy["word"]))
        with open(dyn_config, 'w') as cf:
            yaml.dump(cfy, cf)
        await app.send_message(group, MessageChain(At(event.sender.id), Plain(" OK辣！")))
    except Exception as err:
        await app.send_message(group, MessageChain(At(event.sender.id), Plain(f" 报错辣！{err}")))


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def echo(app: Ariadne, event: MessageEvent):
    if isinstance(event.sender, Member):  # 如果是群聊消息
        wd = jieba.lcut(  # 准确率：分词
            opc.convert(  # 抗混淆：繁简字转换
                str(event.message_chain).strip(' []【】{}\\!！?？啊哦额呃嗯嘿')  # 抗混淆：去除语气词
            )
        )
        for w in wd:
            if w in cache_var.sensitive_words:
                await app.recall_message(event)
                await app.send_message(event.sender.group, MessageChain(
                    [At(event.sender.id), "你的消息涉及敏感内容，为保护群聊消息已被撤回"]))
                await run_sql('UPDATE wd SET count=count+1 WHERE wd=%s', (w,))
                break


@channel.use(ListenerSchema(listening_events=[MessageEvent]))
async def echo(app: Ariadne, event: MessageEvent):
    if isinstance(event.sender, Member):  # 如果是群聊消息
        if event.sender.group.id in botfunc.get_dyn_config('word'):
            wd = jieba.lcut(  # 准确率：分词
                opc.convert(  # 抗混淆：繁简字转换
                    str(event.message_chain).strip(' []【】{}\\!！?？啊哦额呃嗯嘿')  # 抗混淆：去除语气词
                )
            )
            for w in wd:
                if w in cache_var.sensitive_words:
                    await app.recall_message(event)
                    await app.send_message(event.sender.group, MessageChain(
                        [At(event.sender.id), "你的消息涉及敏感内容，为保护群聊消息已被撤回"]))
                    await run_sql('UPDATE wd SET count=count+1 WHERE wd=%s', (w,))
                    break


@listen(GroupMessage)
async def echo(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("加敏感词")):
    try:
        await run_sql('INSERT INTO wd(wd) VALUES (%s)', (message,))
    except Exception as err:
        await app.send_message(event.sender.group, f'寄！{err}')
    else:
        await app.send_message(event.sender.group, f'好辣！')


@listen(GroupMessage)
async def echo(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("删敏感词")):
    try:
        await run_sql('DELETE FROM wd WHERE wd=%s', (message,))
    except Exception as err:
        await app.send_message(event.sender.group, f'寄！{err}')
    else:
        await app.send_message(event.sender.group, f'好辣！')
