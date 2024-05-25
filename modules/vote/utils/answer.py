#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

from arclet.alconna import Args, Arg, CommandMeta, MultiVar, Alconna, Option

vid = Args(Arg("id#投票ID", int))
one_option = Args(Arg("option#选项序号", int))
multiple_option = Args(Arg("options#选项序号", MultiVar(int)))
alternative = Option(
    "--alternative",
    Args(Arg("alternative", MultiVar(int), seps=" ")),
    help_text="备选项，可按顺序传入多个。若是多选投票，那么每个备选项应对于每个主选项的下一个顺位",
    default=[],
)
single = Alconna(
    "单选投票", vid, one_option, alternative,
    meta=CommandMeta(
        "向一个单项选择投票进行投票",
        usage="传入投票ID（即第多少号表决）和一个选项即可，顺序不可颠倒，参数间用空格隔开，多次投票将覆盖上一次的投票",
        example="单选投票 1 3",
    )
)

multiple = Alconna(
    "多选投票", vid, multiple_option,
    meta=CommandMeta(
        "向一个多项选择投票进行投票",
        usage="传入投票ID（即第多少号表决）和一个或多个选项即可，顺序不可颠倒，参数间用空格隔开，多次投票将覆盖上一次的投票",
        example="多选投票 1 3 4 7 8",
    ),
    separators="\n"
)

proportion = Alconna(
    "比重投票", vid, multiple_option, alternative,
    meta=CommandMeta(
        "对一个比重投票进行投票",
        usage="传入投票ID（即第多少号表决）并按照顺序传入每个选项的比重即可，顺序不可颠倒，参数间用空格隔开，多次投票将覆盖上一次的投票",
        example="比重投票 3 12 5 4 9",
    ),
    separators="\n"
)

score = Alconna(
    "评分投票", vid, multiple_option,
    meta=CommandMeta(
        "对一个评分投票机进行投票",
        usage="传入投票ID（即第多少号表决）并按照顺序传入每个选项的评分即可，顺序不可颠倒，参数间用空格隔开，多次投票将覆盖上一次的投票",
        example="评分投票 1 5 5 3 2 1",
    ),
    separators="\n"
)

sort = Alconna(
    "排序投票", vid, multiple_option,
    meta=CommandMeta(
        "对一个排序投票进行投票",
        usage="传入投票ID（即第多少号表决）并按照顺序传入每个选项的排序后对应的序号即可，顺序不可颠倒，参数间用空格隔开，多次投票将覆盖上一次的投票",
        example="排序投票 1 4 5 3 2 1"
    ),
    separators="\n"
)

# 特殊的三个
stop = Alconna(
    "结束投票", vid,
    meta=CommandMeta(
        "结束一个正在进行的投票",
        usage="传入投票ID（即第多少号表决）即可，然后将立刻进行统计，结束后无法再次开启",
        example="结束投票 1"
    ),
    separators="\n"
)
delete = Alconna(
    "删除投票", vid,
    meta=CommandMeta(
        "删除自己的投出的票",
        usage="传入投票ID（即第多少号表决）即可，删除后无法恢复数据",
        example="结束投票 1"
    ),
    separators="\n"
)
close = Alconna(
    "废弃投票", vid,
    meta=CommandMeta(
        "废弃一个投票",
        usage="传入投票ID（即第多少号表决）即可，然后将立刻进行统计，废弃后无法再次开启",
        example="废弃投票 1"
    ),
    separators="\n"
)
