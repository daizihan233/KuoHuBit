---
title: 敏感词检测算法
icon: creative
category:

- 代码品读

---

本篇你会知道机器人是如何检测敏感词的检测逻辑，先上代码：

```Python
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
            await run_sql('UPDATE wd SET count=count+1 WHERE wd=%s', (str(event.message_chain),))
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
                await run_sql('UPDATE wd SET count=count+1 WHERE wd=%s', (w,))
                break
```

太长了？我们挑重点，拆开来看：

```Python
msg = opc.convert(  # 抗混淆：繁简字转换
    str(event.message_chain).strip(' []【】{}\\!！.。…?？啊哦额呃嗯嘿/')  # 抗混淆：去除语气词
)
```

没错，首先机器人利用了opencc开源库对繁体进行了转换，然后去除了语气词与标点符号

```Python
if str(event.message_chain) in cache_var.sensitive_words:
```

如果整句都匹配敏感词则直接撤回

```Python
wd = jieba.lcut(  # 准确率：分词
    msg
)
```

然后通过 jieba 分词，来防止误判，比如将 ```黑夜/总会/过去``` 检测为 ```黑/夜总会/过去```<br>
最后逐一对比敏感词
