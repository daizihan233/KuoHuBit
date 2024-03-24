from typing import Union

from arclet.alconna import Args, Option, Arg, CommandMeta, MultiVar, Alconna


class Problem:
    title = Args(Arg('title#标题', str))
    option = Args(Arg("option#选项", MultiVar(str)))
    deny = Option("--deny", Args(Arg("deny", MultiVar(Union[int, str]), seps=" ")),
                  help_text="阻止这些人参加投票，本群中的人可用 local 表示", default=[])
    accept = Option("--accept", Args(Arg("accept", MultiVar(Union[int, str]), seps=" ")),
                    help_text="仅允许这些人参加投票，本群中的人可用 local 表示", default=[])
    single = Alconna(
        "发起单选投票",
        title, "\n",
        option, "\n",
        deny, "\n",
        accept,
        meta=CommandMeta(
            "发起一个单项选择投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起单选投票\n你玩原神吗？\n不玩\n玩\n原神，启动！\n--deny local 123456 789114 514191",
        ),
    )

    multiple = Alconna(
        "发起多选投票",
        title, "\n",
        option, "\n",
        deny, "\n",
        accept,
        meta=CommandMeta(
            "发起一个多项选择投票",
            usage="传入标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起多选投票\n你玩什么游戏？\n三蹦子\n原神\n星铁\n--deny local 123456 789114 514191",
        ),
    )

    proportion = Alconna(
        "发起比重投票",
        Args(Arg("max#最大比重", int)),
        title, "\n",
        option, "\n",
        deny, "\n",
        accept, "\n",
        Option("--sort", Args(Arg("sort", bool, seps=" ")),
               help_text="是否切换为排序模式，即比重必须为自然数列且不可有重复，值为 True 时开启，默认 False",
               default=False),
        meta=CommandMeta(
            "发起一个单项选择投票",
            usage="传入最大比重标题和选项即可，选项前不必附带序号，参数间使用换行分割，同一参数下多个值使用空格分割",
            example="发起比重投票\n114\n你对以下时代马戏团的人的好感度？\n马+7\n迷你世界\n原神\n--deny local 123456 789114 514191\n--sort True",
        ),
    )


Problem.single.parse("发起单选投票 --help")
Problem.single.parse("发起单选投票")
Problem.single.parse("发起单选投")

print(Problem.single.parse("发起单选投票\n你玩原神吗？\n不玩\n玩\n原神，启动！\n--deny local 123456 789114 514191"))
