#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import json
from typing import Union, Dict, Any

from arclet.alconna import Alconna, Args, Option, Arg, CommandMeta, MultiVar
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.channel import ChannelMeta

import botfunc

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "投票"
channel.meta["description"] = "喝啊，任何邪恶都将绳之以法"
channel.meta["author"] = "KuoHu"


class Problem:
    title = Args(Arg('title#标题', str))
    option = Args(Arg("option#选项", MultiVar(str)))
    deny = Option("--deny", Args(Arg("deny", MultiVar(Union[int, str]), seps=" ")),
                  help_text="阻止这些人参加投票，本群中的人可用 local 表示", default=[])
    accept = Option("--accept", Args(Arg("accept", MultiVar(Union[int, str]), seps=" ")),
                    help_text="仅允许这些人参加投票，本群中的人可用 local 表示", default=[])
    single = Alconna(
        "发起单选投票",
        title,
        option,
        deny,
        meta=CommandMeta(
            "发起一个单项选择投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起单选投票\n你玩原神吗？\n不玩\n玩\n原神，启动！\n--deny local 123456 789114 514191",
        ),
        separators="\n"
    )

    multiple = Alconna(
        "发起多选投票",
        title,
        option,
        deny,
        accept,
        meta=CommandMeta(
            "发起一个多项选择投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起多选投票\n你玩什么游戏？\n三蹦子\n原神\n星铁\n--deny local 123456 789114 514191",
        ),
        separators="\n"
    )

    proportion = Alconna(
        "发起比重投票",
        Args(Arg("max#最大比重", int)),
        title,
        option,
        deny,
        accept,
        Option("--sort", Args(Arg("sort", bool, seps=" ")),
               help_text="是否切换为排序模式，即比重必须为自然数列且不可有重复，值为 True 时开启，默认 False",
               default=False),
        meta=CommandMeta(
            "发起一个单项选择投票",
            usage="传入最大比重标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起比重投票\n114\n你对以下时代马戏团的人的好感度？\n马+7\n迷你世界\n原神\n--deny local 123456 789114 514191\n--sort True",
        ),
        separators="\n"
    )


@alcommand(Problem.single, private=False, send_error=True)
async def initiate_single(app: Ariadne, group: Group, member: Member, title: str, option: list, deny: list,
                          accept: list):
    options: Dict[Any, Any] = {key: 0 for key in option}
    options["deny"] = deny
    options["accept"] = accept
    results = await botfunc.select_fetchall(
        """INSERT INTO vote (gid, uid, type, status, result, title, options) VALUES (%s, %s, 0, false, -1, %s, %s)""",
        (group.id, member.id, title, json.dumps(options))
    )
    opt_str = "\n".join(
        [f"{x[0]}.{x[1]}" for x in enumerate(options, 1)]
    )
    await app.send_group_message(group, f"⟨{results[0]}⟩ 号表决已创建！内容如下：\n"
                                        f"类型：单选投票\n"
                                        f"发起者：{member.id}\n"
                                        f"仅可参加：{accept}\n"
                                        f"不可参加：{deny}\n"
                                        f"标题：{title}\n"
                                        f"选项：\n"
                                        f"{opt_str}\n"
                                 )
