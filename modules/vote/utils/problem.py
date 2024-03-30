#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
from typing import Union

from arclet.alconna import Args, Option, Arg, CommandMeta, MultiVar, Alconna


class Problem:
    title = Args(Arg("title#标题", str))
    option = Args(Arg("option#选项", MultiVar(str)))
    deny = Option(
        "--deny",
        Args(Arg("deny", MultiVar(Union[int, str]), seps=" ")),
        help_text="阻止这些人参加投票，本群中的人可用 local 表示",
        default=[],
    )
    accept = Option(
        "--accept",
        Args(Arg("accept", MultiVar(Union[int, str]), seps=" ")),
        help_text="仅允许这些人参加投票，本群中的人可用 local 表示",
        default=[],
    )
    single = Alconna(
        "发起单选投票",
        title,
        option,
        deny,
        accept,
        meta=CommandMeta(
            "发起一个单项选择投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起单选投票\n"
                    "你玩原神吗？\n"
                    "不玩\n"
                    "玩\n"
                    "原神，启动！\n"
                    "--accept local 123456 789114 514191",
        ),
        separators="\n"
    )

    multiple = Alconna(
        "发起多选投票",
        title,
        option,
        deny,
        accept,
        Option(
            "--max",
            Args(Arg("max", int)),
            help_text="最多可选多少项，-1 代表可全选，默认所有",
            default=-1,
        ),
        Option(
            "--min",
            Args(Arg("max", int)),
            help_text="最少可选多少项，默认为 1",
            default=1,
        ),
        meta=CommandMeta(
            "发起一个多项选择投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起多选投票\n"
                    "你玩什么游戏？\n"
                    "三蹦子\n"
                    "原神\n"
                    "星铁\n"
                    "--accept local 123456 789114 514191",
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
        meta=CommandMeta(
            "发起一个比重投票",
            usage="传入最大比重、标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起比重投票\n"
                    "114\n"
                    "你对以下时代马戏团的人的好感度？\n"
                    "马+7\n"
                    "迷你世界\n"
                    "原神\n"
                    "--accept local 123456 789114 514191",
        ),
        separators="\n"
    )

    score = Alconna(
        "发起评分投票",
        title,
        option,
        deny,
        accept,
        Option(
            "--max",
            Args(Arg("max", int)),
            help_text="最高分，默认 5 分",
            default=5,
        ),
        Option(
            "--min",
            Args(Arg("max", int)),
            help_text="最低分，默认 1 分",
            default=1,
        ),
        Option(
            "--int",
            Args(Arg("max", int)),
            help_text="最低分，默认 1 分",
            default=True,
        ),
        meta=CommandMeta(
            "发起一个评分投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起比重投票\n"
                    "114\n"
                    "你对以下时代马戏团的人的好感度？\n"
                    "马+7\n"
                    "迷你世界\n"
                    "原神\n"
                    "--accept local 123456 789114 514191\n"
                    "--max 10\n"
                    "--min 0\n"
                    "--int True",
        ),
        separators="\n"
    )

    sort = Alconna(
        "发起排序投票",
        title,
        option,
        deny,
        accept,
        meta=CommandMeta(
            "发起一个排序投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起比重投票\n"
                    "114\n"
                    "你对以下时代马戏团的人的好感度？\n"
                    "马+7\n"
                    "迷你世界\n"
                    "原神\n"
                    "--accept local 123456 789114 514191\n"
        ),
        separators="\n"
    )
