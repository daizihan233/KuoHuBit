---
title: 第一步：环境搭建
icon: info
---

本篇主要写了如何搭建必须的环境

# 必须有的

本小节默认你会安装如下软件：（请不要直接安装，读完再安装，有些提示在文章后面）

- Git
- Java
- Redis
- MySQL
- Mirai
- MAH (Mirai-API-HTTP)
- Python
  - pdm

## 关于 Java、Mirai、MAH 的安装

请参考 [GraiaX 文档的这个部分](https://graiax.cn/before/install_mirai.html)

## 关于 Redis、MySQL 的安装

如果你跟我一样 ~~非常懒~~ 那么你可以选择使用 Docker 安装，Redis请不要设置密码（记得堵好端口）

MySQL 建议使用 8.0.31 （我测试时使用的版本，当然也兼容 5.7 版本，你可以看心情选择）

## 关于 Python的安装

```text
Python Version >= 3.10
```

安装 pdm：

```shell
pip install pdm
```

## 如果你遇到 *pip下载慢* / *安装报错* / *找不到pip* / *Python版本错误*

您不会自己百度一下吗？

# 下载 KHB 源码

```shell
git clone https://github.com/daizihan233/KuoHuBit.git
```

请务必使用 `git clone` 否则更新起来会很麻烦

# 依赖安装

```shell
pdm install
```

就好辣！
