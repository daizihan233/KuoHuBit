---
title: 第二步：配置文件
icon: info
---

本篇教你如何配置
::: tips
这篇写了跟没写一样
:::

# cloud.json

见 [github.com@daizihan233/KuoHuBit #17](https://github.com/daizihan233/KuoHuBit/issues/17)

# config.yaml

有写注释，自己看（

# jieba_words.txt

本文件存储了一些敏感词，有些敏感词会被 jieba 错误的断句

比如“你妈死了”一般来说断句为“你妈/死/了”，但是jieba会断句为“你/妈/死/了”

本文件用于增强jieba分词的正确率，你同样可以加一些词

# modules/currency/6.py, line 23

这是一个列表，里面存储了相关的词汇，你可以修改这个列表

请注意：对于汉字和大写数字，还有连续的数字，在预处理中已经做了转换

```python
async def text_pretreatment(s):
    s = s.replace('六', '6').replace('九', '9').replace('陆', '6').replace('玖', '9')
        .replace('(', '（').replace(')', '）')
    replace_words = [
        (r"6+", "6"),
        (r"9+", "9"),
        (r"（+", "（"),
        (r"）+", "）")
    ]
    stop_words = " ，,。.!！？?…^"
    for stop in stop_words:
        s = s.replace(stop, '')
    for regex in replace_words:
        s = re.compile(regex[0]).sub(regex[1], s)
    return s
```

# img/6/

里面是与 6榜 相关的图片，你可以自行添加/删除
