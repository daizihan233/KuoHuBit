---
title: 第一步：环境搭建
icon: info
category:

- 构建指南

---

本篇主要写了如何搭建必须的环境

# 必须有的

本小节默认你会安装如下软件：（请不要直接安装，读完再安装，有些提示在文章后面）

- Java
- Redis
- MySQL
- Mirai
- MAH (Mirai-API-HTTP)
- Python
    - poetry

## 关于 Java、Mirai、MAH 的安装

请参考 [GraiaX 文档的这个部分](https://graiax.cn/before/install_mirai.html)

## 关于 Redis、MySQL 的安装

如果你跟我一样 ~~非常懒~~ 那么你可以选择使用 Docker 安装，Redis请不要设置密码（记得堵好端口）<br>

## 关于 Python、Poetry 的安装

```text
Python Version >= 3.11
Poetry Version >= 1.3.1
```

# 依赖安装

```shell
poetry install
```

就好辣！
