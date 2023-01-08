import random
import time

import pymysql.err
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from botfunc import cursor, conn  # MySQL

channel = Channel.current()
channel.name("赛博木鱼")
channel.description("敲赛博木鱼 ＿＿＿＿＿")
channel.author("HanTools")
get_data_sql = "SELECT * FROM wooden_fish WHERE uid = %s"

"""
本程序的升级经验值计算公式取自 Abjust/2kbot
900 * pow(2, level - 1)
"""


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
        data[4] += round(
            sum(
                [
                    random.randint(-2, 2) for _ in
                    range(int(int(time.time()) - data[1]) // round(pow(data[2], -1) * 10))
                ]
            )
        )
        cursor.execute(
            "UPDATE wooden_fish SET de = %s WHERE uid = %s",
            (data[4], event.sender.id)
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
                        f"木鱼经验：{data[3]}\n"
                        f"当前速度：{pow(data[2], -1) * 10}s/周期\n"
                        f"当前功德：{data[4]}")
                ]
            )
        )
    else:  # 查无此人
        await app.send_message(
            group,
            "赛博数据库查无此人~ 请输入“敲木鱼“注册"
        )


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("敲木鱼")]
    )
)
async def sign(app: Ariadne, group: Group, event: GroupMessage):
    try:
        cursor.execute(
            "INSERT INTO wooden_fish(uid, time, level, exp, de) VALUES (%s, %s, %s, %s, %s)",
            (event.sender.id, int(time.time()), 1, 1, 0)
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
async def update_bread(event: GroupMessage):
    cursor.execute(get_data_sql, (event.sender.id,))
    result = cursor.fetchone()
    if result:
        res = list(result)
        res[3] += random.randint(0, 2)  # 看人品加经验
        if res[3] >= 900 * pow(2, res[2] - 1):
            res[2] += 1
            res[3] = random.randint(0, 2)  # 别问为什么这么写，问就是特色
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
