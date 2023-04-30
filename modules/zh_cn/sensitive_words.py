#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

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
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

import botfunc
import cache_var

channel = Channel.current()
channel.name("敏感词检测")
channel.description("防止群被炸")
channel.author("HanTools")
opc = opencc.OpenCC('t2s')
dyn_config = 'dynamic_config.yaml'
"""
./jieba_words.txt 是什么？
jieba 确实是一个非常不错的分词工具
但在处理诸如“你妈”之类的词的时候并不是很好
“你妈”我们希望被识别为一个词 -> ["你妈"]
但真实情况事“你妈”被识别成了两个词 -> ["你", "妈"]
这当然不是我们想要的效果，此文件是为了让 jieba 更好地处理此类词语而创建的
文件语法为：(词语) [词频] [词性]  | () -> 必选参数，[] -> 可选参数
比如：
极速模式 20
北京清华大学 5
李小福 2 nr
创新办 3 i
easy_install 3 eng
好用 300
韩玉赏鉴 3 nz
八一双鹿 3 nz
台中
凱特琳 nz
Edu Trust认证 2000
"""
jieba.load_userdict("./jieba_words.txt")


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


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def f(app: Ariadne, group: Group, event: GroupMessage):
    if group.id in botfunc.get_dyn_config('word'):
        msg = opc.convert(  # 抗混淆：繁简字转换
            str(event.message_chain).strip(' []【】{}\\!！.。…?？啊哦额呃嗯嘿/')  # 抗混淆：去除语气词
        )
        if str(event.message_chain) in cache_var.sensitive_words:  # 准确率：整句匹配
            try:
                await app.recall_message(event)
            except PermissionError:
                logger.error('无权操作！')
            else:
                await app.send_message(event.sender.group, MessageChain(
                    [At(event.sender.id), "你的消息涉及敏感内容，为保护群聊消息已被撤回"]))
            await botfunc.run_sql('UPDATE wd SET count=count+1 WHERE wd=%s', (str(event.message_chain),))
            return
        wd = jieba.lcut(  # 准确率：分词
            msg
        )
        logger.debug(wd)
        for w in wd:
            if w in cache_var.sensitive_words:
                try:
                    await app.recall_message(event)
                except PermissionError:
                    logger.error('无权操作！')
                else:
                    await app.send_message(event.sender.group, MessageChain(
                        [At(event.sender.id), "你的消息涉及敏感内容，为保护群聊消息已被撤回"]))
                await botfunc.run_sql('UPDATE wd SET count=count+1 WHERE wd=%s', (w,))
                break


@listen(GroupMessage)
async def add(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("加敏感词")):
    if event.sender.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        if str(message) not in cache_var.sensitive_words:
            try:
                await botfunc.run_sql('INSERT INTO wd(wd) VALUES (%s)', (message,))
            except Exception as err:
                await app.send_message(event.sender.group, f'寄！{err}')
            else:
                await app.send_message(event.sender.group, '好辣！')
            try:
                cache_var.sensitive_words.append(str(message))
            except Exception as err:
                logger.error(err)
        else:
            await app.send_message(event.sender.group, '有没有一种可能，这个词已经加过了')


@listen(GroupMessage)
async def rm(app: Ariadne, event: GroupMessage, message: MessageChain = DetectPrefix("删敏感词")):
    if event.sender.permission in [MemberPerm.Administrator, MemberPerm.Owner]:
        try:
            await botfunc.run_sql('DELETE FROM wd WHERE wd=%s', (message,))
        except Exception as err:
            await app.send_message(event.sender.group, f'寄！{err}')
        else:
            await app.send_message(event.sender.group, '好辣！')
        try:
            cache_var.sensitive_words.remove(str(message))
        except Exception as err:
            logger.error(err)
