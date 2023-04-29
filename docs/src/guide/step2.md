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

```python
sl1 = ["6", "9", "6的", "9（6翻了）", "⑥", "₆", "⑹", "⒍", "⁶", "陆", "Six", "Nine", "\u0039\ufe0f\u20e3",
       "\u0036\ufe0f\u20e3", "♸"]
```

你可以自行向此列表添加词汇，但是请注意，因为算法的原因，过多的添加会导致出现很多误判
