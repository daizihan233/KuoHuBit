import asyncio
import random
import time

import aiomysql
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent, MatchRegex
from graia.ariadne.model import Group
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

import botfunc
from modules.wooden_fish import get_data_sql, ban_cache, forever_ban_cache, details_cache

channel = Channel.current()
channel.name("賽博木魚")
channel.description("敲賽博木魚 ＿＿＿＿＿")
channel.author("HanTools")
loop = asyncio.get_event_loop()


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
    return r


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
@decorate(MatchContent("我的木魚"))
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
        if event.sender.id not in ban_cache and not data[5]:
            data = list(data)
            data[4] += int(int(int(time.time()) - data[1]) / (pow(data[2], -1) * 60))
            await else_sql(
                "UPDATE wooden_fish SET time = unix_timestamp(now()) , de = %s WHERE uid = %s",
                (data[4], event.sender.id)
            )
            result = await select_fetchone(get_data_sql, (event.sender.id,))
            if (int(time.time()) - result[7]) < botfunc.get_config('count_ban'):
                await else_sql(
                    "UPDATE wooden_fish SET end_count = wooden_fish.end_count+1 WHERE uid = %s", (event.sender.id,)
                )
            else:
                await else_sql(
                    "UPDATE wooden_fish SET end=%s, end_count = 0 WHERE uid = %s",
                    (int(time.time()), event.sender.id)
                )
            if int(time.time()) - result[7] <= botfunc.get_config('count_ban') and 5 <= result[8]:
                ban_cache.append(event.sender.id)
                await app.send_group_message(
                    group.id,
                    [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小时")]
                )
                await else_sql(
                    "UPDATE wooden_fish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                    (event.sender.id,)
                )
                return

        else:
            logger.debug(f'data[5] -> {data[5]}')

            if data[5] == 1:
                status = '封禁中 | 永久'
                flag = True
                flag2 = True
            elif data[5] == 2:
                if int(time.time()) < data[6]:
                    status = f'封禁中 | 直至 {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data[6]))}'
                    flag = True
                else:
                    status = '正常'
                    await else_sql(
                        "UPDATE wooden_fish SET ban=0, time = %s, dt=0, end=0, end_count=0 WHERE uid = %s",
                        (int(time.time()), event.sender.id)
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
            await app.send_message(
                group,
                MessageChain(
                    [
                        At(event.sender.id),
                        Plain(
                            f"\n"
                            f"賽博賬號：{event.sender.id}\n"
                            f"賬號狀態：{status}\n"
                            f"木魚等級：{data[2]}\n"
                            f"木魚經驗：{data[3]} / {int(100 * (pow(1.14, data[2] - 1)))}\n"
                            f"當前速度：{round(pow(data[2], -1) * 10, 2)}s/週期\n"
                            f"當前功德：{data[4]}\n"
                            f"{'【Tips：封禁後如果要解禁請發送“我的木魚”以刷新狀態】' if data[5] else '【敲電子木魚，見機甲佛祖，取賽博真經】'}")
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
            " 賽博數據庫查無此人~ 請輸入“給我木魚”註冊"
        )


@listen(GroupMessage)
@decorate(MatchContent("給我木魚"))
async def sign(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        result = await select_fetchone(get_data_sql, (event.sender.id,))
        if result is not None:
            if int(time.time()) - result[7] <= botfunc.get_config('count_ban') and 5 <= result[8]:
                ban_cache.append(event.sender.id)
                await app.send_group_message(
                    group.id,
                    [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小時")]
                )
                await else_sql(
                    "UPDATE wooden_fish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                    (event.sender.id,)
                )
                return
        try:
            await else_sql(
                "INSERT INTO wooden_fish(uid, time, level, exp, de, ban, dt, end, end_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (event.sender.id, int(time.time()), 1, 1, random.randint(1000, 2000), 0, 0, 0, 0)
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
                "你不是註冊過了嗎？"
            )
            result = await select_fetchone(get_data_sql, (event.sender.id,))
            if (int(time.time()) - result[7]) < botfunc.get_config('count_ban'):
                await else_sql(
                    "UPDATE wooden_fish SET end_count = wooden_fish.end_count+1 WHERE uid = %s", (event.sender.id,)
                )
            else:
                await else_sql(
                    "UPDATE wooden_fish SET end=%s, end_count = 0 WHERE uid = %s",
                    (int(time.time()), event.sender.id)
                )


@listen(GroupMessage)
@decorate(MatchContent("敲木魚"))
async def update_wf(app: Ariadne, group: Group, event: GroupMessage):
    if event.sender.id not in ban_cache:
        result = await select_fetchone(get_data_sql, (event.sender.id,))
        if result:
            if not result[5]:
                res = list(result)
                if int(time.time()) - res[7] <= botfunc.get_config('count_ban') and 5 <= res[8]:
                    ban_cache.append(event.sender.id)
                    await app.send_group_message(
                        group.id,
                        [At(event.sender.id), Plain(f" 您疑似DoS佛祖，被封禁 1 小時")]
                    )
                    await else_sql(
                        "UPDATE wooden_fish SET ban=2, dt = unix_timestamp(now()) + 3600 WHERE uid = %s",
                        (event.sender.id,)
                    )
                else:
                    rad = random.randint(1, 5)
                    await app.send_message(
                        group,
                        [At(event.sender.id), Plain(f" 功德 +{rad}")]
                    )
                    if (int(time.time()) - result[7]) < botfunc.get_config('count_ban'):
                        await else_sql(
                            "UPDATE wooden_fish SET end_count = wooden_fish.end_count+1 WHERE uid = %s",
                            (event.sender.id,)
                        )
                    else:
                        await else_sql(
                            "UPDATE wooden_fish SET end=%s, end_count = 0 WHERE uid = %s",
                            (int(time.time()), event.sender.id)
                        )
                    await else_sql("UPDATE wooden_fish SET de = de + %s WHERE uid = %s", (rad, event.sender.id))

            else:
                ban_cache.append(event.sender.id)
                await app.send_message(
                    group,
                    [At(event.sender.id), Plain(f" 你已被佛祖封禁")]
                )

        else:  # 查无此人
            await app.send_message(
                group,
                [At(event.sender.id), Plain(" 賽博數據庫查無此人~ 請輸入“給我木魚”註冊")]
            )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchRegex("1+")]
    )
)
async def subtract_gd(app: Ariadne, group: Group, message: MessageChain, event: GroupMessage):
    if event.sender.id not in ban_cache:
        gd = str(message).count("1")
        try:
            await else_sql("UPDATE wooden_fish SET de=de-wooden_fish.level*10*%s WHERE uid=%s",
                           (gd, event.sender.id,))
            await app.send_message(group, f"佛祖：{'哈 * ' + str(gd) if gd > 50 else '哈' * gd}（功德 -{gd * 10}）")
        except Exception as err:
            logger.error(err)
