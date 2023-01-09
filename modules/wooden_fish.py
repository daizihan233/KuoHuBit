import random
import time

import pymysql.err
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.event.mirai import NudgeEvent
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

import botfunc
from botfunc import cursor, conn  # MySQL

channel = Channel.current()
channel.name("赛博木鱼")
channel.description("敲赛博木鱼 ＿＿＿＿＿")
channel.author("HanTools")
get_data_sql = "SELECT * FROM wooden_fish WHERE uid = %s"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("我的木鱼")]
    )
)
async def my_wf(app: Ariadne, group: Group, event: GroupMessage):
    cursor.execute(
        get_data_sql,
        (event.sender.id,)
    )
    data = cursor.fetchone()  # 只可能返回一个数据
    if data:  # 如果在数据库中
        data = list(data)
        data[4] += int((int(int(time.time()) - data[1])) / (pow(data[2], -1) * 10))
        # 防止出现负数
        while data[4] < 0:
            data[4] += int((int(int(time.time()) - data[1])) / (pow(data[2], -1) * 10))
        cursor.execute(
            "UPDATE wooden_fish SET time = %s , de = %s WHERE uid = %s",
            (int(time.time()), data[4], event.sender.id)
        )
        await app.send_message(
            group,
            MessageChain(
                [
                    At(event.sender.id),
                    Plain(
                        f"\n"
                        f"赛博账号：{event.sender.id}\n"
                        f"木鱼等级：{data[2]}\n"
                        f"木鱼经验：{data[3]} / {int(100 * (pow(1.14, data[2] - 1)))}\n"
                        f"当前速度：{round(pow(data[2], -1) * 10, 2)}s/周期\n"
                        f"当前功德：{data[4]}")
                ]
            )
        )
    else:  # 查无此人
        await app.send_message(
            group,
            "赛博数据库查无此人~ 请输入“给我木鱼”注册"
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("给我木鱼")]
    )
)
async def sign(app: Ariadne, group: Group, event: GroupMessage):
    try:
        cursor.execute(
            "INSERT INTO wooden_fish(uid, time, level, exp, de) VALUES (%s, %s, %s, %s, %s)",
            (event.sender.id, int(time.time()), 1, 1, random.randint(1000, 2000))
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
    except pymysql.err.IntegrityError:
        await app.send_message(
            group,
            "你不是注册过了吗？"
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def update_wf(event: GroupMessage):
    cursor.execute(get_data_sql, (event.sender.id,))
    result = cursor.fetchone()
    if result:
        res = list(result)
        res[3] += random.randint(1, 5)  # 看人品加经验
        if res[3] >= int(100 * (pow(1.14, res[2] - 1))):
            res[2] += 1
            res[3] = random.randint(1, 5)  # 别问为什么这么写，问就是特色
            cursor.execute(
                "UPDATE wooden_fish SET level = %s, exp = %s WHERE uid = %s",
                (res[2], res[3], event.sender.id)
            )
            conn.commit()
        else:
            cursor.execute(
                "UPDATE wooden_fish SET exp = %s WHERE uid = %s",
                (res[3], event.sender.id)
            )
            conn.commit()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("敲木鱼")]
    )
)
async def update_wf(app: Ariadne, group: Group, event: GroupMessage):
    cursor.execute(get_data_sql, (event.sender.id,))
    result = cursor.fetchone()
    if result:
        res = list(result)
        rad = random.randint(1, 5)
        res[4] += rad  # 看人品加功德
        cursor.execute(
            "UPDATE wooden_fish SET de = %s WHERE uid = %s",
            (res[4], event.sender.id)
        )
        conn.commit()
        await app.send_message(
            group,
            f"功德 +{rad}"
        )
    else:  # 查无此人
        await app.send_message(
            group,
            "赛博数据库查无此人~ 请输入“给我木鱼”注册"
        )


@channel.use(ListenerSchema(listening_events=[NudgeEvent]))
async def getup(app: Ariadne, event: NudgeEvent):
    if event.target == botfunc.get_config('qq'):
        if event.context_type == "group":
            logger.info(f"{event.supplicant} 在群 {event.group_id} 戳了戳 Bot")
            cursor.execute(get_data_sql, (event.supplicant,))
            result = cursor.fetchone()
            if result:
                res = list(result)
                rad = random.randint(1, 5)
                res[4] += rad  # 看人品加功德
                cursor.execute(
                    "UPDATE wooden_fish SET de = %s WHERE uid = %s",
                    (res[4], event.supplicant)
                )
                conn.commit()
                await app.send_group_message(
                    event.group_id,
                    f"功德 +{rad}"
                )
            else:  # 查无此人
                await app.send_group_message(
                    event.group_id,
                    "赛博数据库查无此人~ 请输入“给我木鱼”注册"
                )
        else:
            logger.warning('不是群内戳一戳')
    else:
        logger.warning('戳了戳别人')
