---
title: 投票系统
icon: info
---

# 发起

## 发起一个单项选择投票

### 指令:

**发起单选投票&lt;title: str&gt; &lt;option: (str+)&gt;**

### 注释:

```
title: 标题
option: 选项
```

传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割

### 可用的选项有:

- **--deny &lt;deny: (int|str+)&gt;**

> 阻止这些人参加投票，本群中的人可用 local 表示

- **--accept &lt;accept: (int|str+)&gt;**

> 仅允许这些人参加投票，本群中的人可用 local 表示

### 使用示例:

```
发起单选投票
你玩原神吗？
不玩
玩
原神，启动！
--deny local 123456 789114 514191
```

## 发起一个多项选择投票

### 指令:

**发起多选投票&lt;title: str&gt; &lt;option: (str+)&gt;**

### 注释:
```
title: 标题
option: 选项
```

传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割

### 可用的选项有:
- **--deny &lt;deny: (int|str+)&gt;**
> 阻止这些人参加投票，本群中的人可用 local 表示

- **--accept &lt;accept: (int|str+)&gt;**
> 仅允许这些人参加投票，本群中的人可用 local 表示

- **--max &lt;max: int&gt;**

> 最多可选多少项，-1 代表可全选，默认所有

- **--min &lt;max: int&gt;**

> 最少可选多少项，默认为 1

### 使用示例:
```shell
发起多选投票
你玩什么游戏？
三蹦子
原神
星铁
--deny local 123456 789114 514191
--max 2
```

## 发起一个比重/排序投票

### 指令:

**发起比重投票 &lt;max: int&gt; &lt;title: str&gt; &lt;option: (str+)&gt;**

### 注释:

```
max: 最大比重
title: 标题
option: 选项
```

传入最大比重标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割

### 可用的选项有:

- **--deny &lt;deny: (int|str+)&gt;**

> 阻止这些人参加投票，本群中的人可用 local 表示

- **--accept &lt;accept: (int|str+)&gt;**

> 仅允许这些人参加投票，本群中的人可用 local 表示

- **--sort &lt;sort: bool&gt;**

> 是否切换为排序模式，即比重必须为自然数列且不可有重复，值为 True 时开启，默认 False

### 使用示例:

```
发起比重投票
114
你对以下时代马戏团的人的好感度？
马+7
迷你世界
原神
--deny local 123456 789114 514191
--sort True
```
