import asyncio
import random
import time

import aiomysql
import numpy as np
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

import botfunc

channel = Channel.current()
channel.name("赛博木鱼")
channel.description("敲赛博木鱼 ＿＿＿＿＿")
channel.author("HanTools")
get_data_sql = "SELECT uid, time, level, de, e, ee, nirvana, ban, dt, end_time, hit_count FROM woodenfish WHERE uid = %s"
loop = asyncio.get_event_loop()
ban_cache = []  # 被ban人员缓存
details_cache = []
forever_ban_cache = []


async def select_fetchone(sql, arg=None):
    conn = await aiomysql.connect(host=botfunc.get_cloud_config('MySQL_Host'),
                                  port=botfunc.get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=botfunc.get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    r = await cur.fetchone()
    await cur.close()
    conn.close()
    return list(r) if r else None


async def else_sql(sql, arg):
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
@decorate(MatchContent("我的木鱼"))
async def my_wf(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id in forever_ban_cache:
        return
    data = await select_fetchone(
        get_data_sql,
        (event.sender.id,)
    )
    logger.debug(data)
    status = '正常'
    flag = False
    flag2 = False
    if data:  # 如果在数据库中
        if event.sender.id not in ban_cache and not data[7]:
            data = list(data)
            data[4] += int(int(int(time.time()) - data[1]) / (60 * np.power(0.95, data[2]))) * (
                        data[4] * data[6] + data[2])
            await else_sql(
                "UPDATE woodenfish SET time = unix_timestamp(now()) , de = %s WHERE uid = %s",
                (data[4], event.sender.id)
            )
            result = await select_fetchone(get_data_sql, (event.sender.id,))
            if (int(time.time()) - result[9]) < botfunc.get_config('count_ban'):
                await else_sql(
                    "UPDATE woodenfish SET hit_count = woodenfish.hit_count+1 WHERE uid = %s", (event.sender.id,)
                )
            else:
                await else_sql(
                    "UPDATE woodenfish SET end_time=unix_timestamp(now()), hit_count = 0 WHERE uid = %s",
                    (event.sender.id,)
                )
            if int(time.time()) - result[9] <= botfunc.get_config('count_ban') and 5 <= result[10]:
                ban_cache.append(event.sender.id)
                await app.send_group_message(
                    group.id,
                    [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                )
                await else_sql(
                    "UPDATE woodenfish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                    (event.sender.id,)
                )
                return

        else:
            logger.debug(f'data[7] -> {data[7]}')

            if data[7] == 1:
                status = '封禁中 | 永久'
                flag = True
                flag2 = True
            elif data[7] == 2:
                if int(time.time()) < data[9]:
                    status = f'封禁中 | 直至 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data[8]))}'
                    flag = True
                else:
                    status = '正常'
                    await else_sql(
                        "UPDATE woodenfish SET ban=0, time = unix_timestamp(now()), dt=0, end_time=0, hit_count=0 WHERE uid = %s",
                        (event.sender.id,)
                    )
                    try:
                        ban_cache.remove(event.sender.id)
                    except ValueError:
                        logger.warning("ban_cache: ValueError")
                    try:
                        details_cache.remove(event.sender.id)
                    except ValueError:
                        logger.warning("details_cache: ValueError")

        if event.sender.id not in forever_ban_cache and event.sender.id not in details_cache:
            if np.log10(data[3]) >= 1:
                data[4] = np.log10(np.power(10, data[4]) + data[3])
                await else_sql("UPDATE woodenfish SET e = %s, de = 0 WHERE uid = %s",
                               (data[4], event.sender.id))
            if np.log10(data[4]) >= 1:
                data[5] = np.log10(np.power(10, data[5]) + data[4])
                await else_sql("UPDATE woodenfish SET ee = %s, e = 0 WHERE uid = %s",
                               (data[5], event.sender.id))
            if data[5] >= 1:
                gongde = "ee%.3f （=10^10^%.3f）" % (data[5], data[5])
            elif data[4] >= 1:
                gongde = "e%.3f （=10^%.3f）" % (data[4], data[4])
            else:
                gongde = f"{data[3]}"
            await app.send_message(
                group,
                MessageChain(
                    [
                        At(event.sender.id),
                        Plain(
                            f"\n"
                            f"赛博账号：{event.sender.id}\n"
                            f"账号状态：{status}\n"
                            f"木鱼等级：{data[2]}\n"
                            f"涅槃值　：{data[6]}\n"
                            f"当前速度：{round(pow(data[2], -1) * 10, 2)}s/周期\n"
                            f"当前功德：{gongde}\n"
                            f"{'【Tips：封禁后如果要解禁请发送“我的木鱼”以刷新状态】' if data[7] else '【敲电子木鱼，见机甲佛祖，取赛博真经】'}")
                    ]
                )
            )
            if flag:
                details_cache.append(event.sender.id)
            if flag2:
                forever_ban_cache.append(event.sender.id)
    else:  # 查无此人
        await app.send_message(
            group,
            "赛博数据库查无此人~ 请输入“给我木鱼”注册"
        )


@listen(GroupMessage)
@decorate(MatchContent("给我木鱼"))
async def sign(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        result = await select_fetchone(get_data_sql, (event.sender.id,))
        if result is not None:
            if int(time.time()) - result[9] <= botfunc.get_config('count_ban') and 5 <= result[10]:
                ban_cache.append(event.sender.id)
                await app.send_group_message(
                    group.id,
                    [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                )
                await else_sql(
                    "UPDATE woodenfish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                    (event.sender.id,)
                )
                return
        # --- 从这里开始是进行处理 ---
        try:
            await else_sql(
                "INSERT INTO woodenfish(uid, time) VALUES (%s, unix_timestamp(now()))",
                (event.sender.id,)
            )
            await app.send_message(
                group,
                MessageChain(
                    [
                        Plain(
                            "OK！"
                        )
                    ]
                )
            )
            return
        except Exception as err:
            logger.warning(err)
            await app.send_message(
                group,
                "你不是注册过了吗？"
            )
            result = await select_fetchone(get_data_sql, (event.sender.id,))
            if (int(time.time()) - result[9]) < botfunc.get_config('count_ban'):
                await else_sql(
                    "UPDATE woodenfish SET hit_count = woodenfish.hit_count+1 WHERE uid = %s", (event.sender.id,)
                )
            else:
                await else_sql(
                    "UPDATE woodenfish SET end_time=unix_timestamp(now()), hit_count = 0 WHERE uid = %s",
                    (event.sender.id,)
                )


@listen(GroupMessage)
@decorate(MatchContent("敲木鱼"))
async def update_wf(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        result = await select_fetchone(get_data_sql, (event.sender.id,))
        if result:
            if not result[7]:
                res = list(result)
                if int(time.time()) - res[9] <= botfunc.get_config('count_ban') and 5 <= res[10]:
                    ban_cache.append(event.sender.id)
                    await app.send_group_message(
                        group.id,
                        [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                    )
                    await else_sql(
                        "UPDATE woodenfish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                        (event.sender.id,)
                    )
                else:
                    # --- 从这里开始是进行处理 ---
                    rad = random.choice([1, 4, 5])
                    await app.send_message(
                        group,
                        [At(event.sender.id), Plain(f" 功德 +{rad}")]
                    )
                    if (int(time.time()) - result[9]) < botfunc.get_config('count_ban'):
                        await else_sql(
                            "UPDATE woodenfish SET hit_count = woodenfish.hit_count+1 WHERE uid = %s",
                            (event.sender.id,)
                        )
                    else:
                        await else_sql(
                            "UPDATE woodenfish SET end_time=unix_timestamp(now()), hit_count = 0 WHERE uid = %s",
                            (event.sender.id,)
                        )
                    await else_sql("UPDATE woodenfish SET de = de + %s WHERE uid = %s", (rad, event.sender.id))
            else:
                ban_cache.append(event.sender.id)
                await app.send_message(
                    group,
                    [At(event.sender.id), Plain(f" 你已被佛祖封禁")]
                )

        else:  # 查无此人
            await app.send_message(
                group,
                [At(event.sender.id), Plain(" 赛博数据库查无此人~ 请输入“给我木鱼”注册")]
            )


@channel.use(ListenerSchema(listening_events=[NudgeEvent]))
async def getup(app: Ariadne, event: NudgeEvent):
    if event.target == botfunc.get_config('qq'):
        if event.context_type == "group":
            logger.info(f"{event.supplicant} 在群 {event.group_id} 戳了戳 Bot")
            result = await select_fetchone(get_data_sql, (event.supplicant,))
            logger.debug(result)
            if result:
                if event.supplicant not in ban_cache:
                    if not result[7]:
                        res = list(result)
                        if int(time.time()) - res[9] <= botfunc.get_config('count_ban') and 5 <= res[10]:
                            ban_cache.append(event.supplicant)
                            await app.send_group_message(
                                event.group_id,
                                [At(event.supplicant), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                            )
                            await else_sql(
                                "UPDATE woodenfish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                                (event.supplicant,)
                            )
                        else:
                            rad = random.choice([1, 4, 5])

                            await app.send_group_message(
                                event.group_id,
                                [At(event.supplicant), Plain(f" 功德 +{rad}")]
                            )
                            if (int(time.time()) - result[9]) < botfunc.get_config('count_ban'):
                                await else_sql(
                                    "UPDATE woodenfish SET hit_count = woodenfish.hit_count+1 WHERE uid = %s",
                                    (event.supplicant,)
                                )
                            else:
                                await else_sql(
                                    "UPDATE woodenfish SET end_time=unix_timestamp(now()), hit_count = 0 WHERE uid = %s",
                                    (event.supplicant,)
                                )
                            await else_sql("UPDATE woodenfish SET de = de + %s WHERE uid = %s",
                                           (rad, event.supplicant))

                    else:
                        ban_cache.append(event.supplicant)
                        await app.send_group_message(
                            event.supplicant,
                            [At(event.supplicant), Plain(f" 你已被佛祖封禁")]
                        )
                else:
                    if result[7] == 2:
                        await else_sql("UPDATE woodenfish SET dt = unix_timestamp(now()) + 360 WHERE uid = %s",
                                       (event.supplicant,))

            else:  # 查无此人
                await app.send_group_message(
                    event.group_id,
                    [At(event.supplicant), Plain(" 赛博数据库查无此人~ 请输入“给我木鱼”注册")]
                )
        else:
            logger.warning('不是群内戳一戳')
    else:
        logger.warning('戳了戳别人')


@listen(GroupMessage)
@decorate(MatchContent("撅佛祖"))  # [简]繁体与简体写法一致 | [繁]繁體與簡體寫法一致
async def jue_fo(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        await else_sql("UPDATE woodenfish SET ban=1 WHERE uid=%s",
                       (event.sender.id,))
        await app.send_message(group, "敢撅佛祖？我给你ban咯！")
        ban_cache.append(event.sender.id)


@listen(GroupMessage)
@decorate(MatchContent("升级木鱼"))
async def update_fish(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        result = await select_fetchone(get_data_sql, (event.sender.id,))
        if result:
            if not result[7]:
                res = list(result)
                if int(time.time()) - res[9] <= botfunc.get_config('count_ban') and 5 <= res[10]:
                    ban_cache.append(event.sender.id)
                    await app.send_group_message(
                        group.id,
                        [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                    )
                    await else_sql(
                        "UPDATE woodenfish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                        (event.sender.id,)
                    )
                else:
                    if np.power(10, result[5]) + result[4] >= result[2] + 2:
                        await else_sql("UPDATE woodenfish SET level = level+1, e = e-level+2 WHERE uid = @uid",
                                       (event.sender.id,))
                        await app.send_message(
                            group,
                            "木鱼升级成功辣！（喜）"
                        )
                    else:
                        result[4] += int(int(int(time.time()) - result[1]) / (60 * np.power(0.95, result[2]))) * (
                                result[4] * result[6] + result[2])
                        if np.log10(result[3]) >= 1:
                            result[4] = np.log10(np.power(10, result[4]) + result[3])
                            await else_sql("UPDATE woodenfish SET e = %s, de = 0 WHERE uid = %s",
                                           (result[4], event.sender.id))
                        if np.log10(result[4]) >= 1:
                            result[5] = np.log10(np.power(10, result[5]) + result[4])
                            await else_sql("UPDATE woodenfish SET ee = %s, e = 0 WHERE uid = %s",
                                           (result[5], event.sender.id))
                        if np.power(10, result[5]) + result[4] >= result[2] + 2:
                            await else_sql("UPDATE woodenfish SET level = level+1, e = e-level+2 WHERE uid = @uid",
                                           (event.sender.id,))
                            await app.send_message(
                                group,
                                "木鱼升级成功辣！（喜）"
                            )
                        else:
                            await app.send_message(
                                group,
                                "宁踏马功德不够，升级个毛啊（恼）"
                            )
        else:  # 查无此人
            await app.send_group_message(
                group.id,
                [At(event.sender.id), Plain(" 赛博数据库查无此人~ 请输入“给我木鱼”注册")]
            )


@listen(GroupMessage)
@decorate(MatchContent("涅槃转生"))
async def update_fish(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        result = await select_fetchone(get_data_sql, (event.sender.id,))
        if result:
            if not result[7]:
                res = list(result)
                if int(time.time()) - res[9] <= botfunc.get_config('count_ban') and 5 <= res[10]:
                    ban_cache.append(event.sender.id)
                    await app.send_group_message(
                        group.id,
                        [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                    )
                    await else_sql(
                        "UPDATE woodenfish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                        (event.sender.id,)
                    )
                else:
                    if result[5] >= 10 * result[6]:
                        await else_sql(
                            "UPDATE woodenfish SET nirvana = nirvana+0.05, level = 0, ee = 0, e = 0, de = 0 WHERE uid = @uid",
                            (event.sender.id,))
                        await app.send_message(
                            group,
                            "转生成功，功德圆满（喜）"
                        )
                    else:
                        result[4] += int(int(int(time.time()) - result[1]) / (60 * np.power(0.95, result[2]))) * (
                                result[4] * result[6] + result[2])
                        if np.log10(result[3]) >= 1:
                            result[4] = np.log10(np.power(10, result[4]) + result[3])
                            await else_sql("UPDATE woodenfish SET e = %s, de = 0 WHERE uid = %s",
                                           (result[4], event.sender.id))
                        if np.log10(result[4]) >= 1:
                            result[5] = np.log10(np.power(10, result[5]) + result[4])
                            await else_sql("UPDATE woodenfish SET ee = %s, e = 0 WHERE uid = %s",
                                           (result[5], event.sender.id))
                        if result[5] >= 10 * result[6]:
                            await else_sql(
                                "UPDATE woodenfish SET nirvana = nirvana+0.05, level = 0, ee = 0, e = 0, de = 0 WHERE uid = @uid",
                                (event.sender.id,))
                            await app.send_message(
                                group,
                                "转生成功，功德圆满（喜）"
                            )
                        else:
                            await app.send_message(
                                group,
                                "宁功德不够，转生个毛啊（恼）"
                            )
        else:  # 查无此人
            await app.send_group_message(
                group.id,
                [At(event.sender.id), Plain(" 赛博数据库查无此人~ 请输入“给我木鱼”注册")]
            )
