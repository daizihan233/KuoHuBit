#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import json

from arclet.alconna import Arparma
from arclet.alconna.graia import AlconnaDispatcher, AlconnaSchema
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.model import Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta
from loguru import logger

import botfunc
from .utils import problem, answer

channel = Channel[ChannelMeta].current()
channel.meta["name"] = "投票"
channel.meta["description"] = "喝啊，任何邪恶都将绳之以法"
channel.meta["author"] = "KuoHu"

GET_MAX_ID = "SELECT MAX(ids) FROM vote"


@channel.use(AlconnaSchema(AlconnaDispatcher(problem.single, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_single(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    opt_args = result.other_args
    options = {
        "options": {key: 0 for key in main_args["option"]},
        "deny": opt_args.get("deny", []),
        "accept": opt_args.get("accept", [])}

    await botfunc.run_sql(
        """INSERT INTO vote (gid, uid, type, status, result, title, options) VALUES (%s, %s, 0, false, -1, %s, %s);""",
        (group.id, member.id, main_args["title"], json.dumps(options, ensure_ascii=False)),
    )
    results = await botfunc.select_fetchone(
        GET_MAX_ID
    )

    opt_str = "\n".join([f"{x[0]}.{x[1]}" for x in enumerate(options["options"].keys(), 1)])
    send_msg = (
        f"⟨{results[0]}⟩ 号表决已创建！内容如下：\n"
        f"类型：单选投票\n"
        f"发起者：{member.id}\n"
        f"仅可参加：{options['accept']}\n"
        f"不可参加：{options['deny']}\n"
        f"标题：{main_args['title']}\n"
        f"选项：\n"
        f"{opt_str}"
    )
    await app.send_group_message(group, send_msg)


@channel.use(AlconnaSchema(AlconnaDispatcher(problem.multiple, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_single(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    opt_args = result.other_args
    options = {
        "options": {key: 0 for key in main_args["option"]},
        "deny": opt_args.get("deny", []),
        "accept": opt_args.get("accept", []),
        "max": opt_args.get("max", -1),
        "min": opt_args.get("min", 1)
    }

    await botfunc.run_sql(
        """INSERT INTO vote (gid, uid, type, status, result, title, options) VALUES (%s, %s, 1, false, -1, %s, %s);""",
        (group.id, member.id, main_args["title"], json.dumps(options, ensure_ascii=False)),
    )
    results = await botfunc.select_fetchone(
        GET_MAX_ID
    )

    opt_str = "\n".join([f"{x[0]}.{x[1]}" for x in enumerate(options["options"].keys(), 1)])
    send_msg = (
        f"⟨{results[0]}⟩ 号表决已创建！内容如下：\n"
        f"类型：多选投票\n"
        f"发起者：{member.id}\n"
        f"仅可参加：{options['accept']}\n"
        f"不可参加：{options['deny']}\n"
        f"最多可选：{'全部' if options['max'] == -1 else options['max']} 项\n"
        f"最少需选：{options['min']} 项\n"
        f"标题：{main_args['title']}\n"
        f"选项：\n"
        f"{opt_str}"
    )
    await app.send_group_message(group, send_msg)


@channel.use(AlconnaSchema(AlconnaDispatcher(problem.proportion, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_single(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    opt_args = result.other_args
    options = {
        "options": {key: 0 for key in main_args["option"]},
        "deny": opt_args.get("deny", []),
        "accept": opt_args.get("accept", []),
        "max": main_args["max"]
    }

    await botfunc.run_sql(
        """INSERT INTO vote (gid, uid, type, status, result, title, options) VALUES (%s, %s, 2, false, -1, %s, %s);""",
        (group.id, member.id, main_args["title"], json.dumps(options, ensure_ascii=False)),
    )
    results = await botfunc.select_fetchone(
        GET_MAX_ID
    )

    opt_str = "\n".join([f"{x[0]}.{x[1]}" for x in enumerate(options["options"].keys(), 1)])
    send_msg = (
        f"⟨{results[0]}⟩ 号表决已创建！内容如下：\n"
        f"类型：比重投票\n"
        f"发起者：{member.id}\n"
        f"仅可参加：{options['accept']}\n"
        f"不可参加：{options['deny']}\n"
        f"模式：{'排序' if options['sort'] else '比重'}\n"
        f"可分配：{options['max']}\n"
        f"标题：{main_args['title']}\n"
        f"选项：\n"
        f"{opt_str}"
    )
    await app.send_group_message(group, send_msg)


@channel.use(AlconnaSchema(AlconnaDispatcher(problem.score, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_score(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    opt_args = result.other_args
    options = {
        "options": {key: 0 for key in main_args["option"]},
        "deny": opt_args.get("deny", []),
        "accept": opt_args.get("accept", []),
        "max": opt_args.get("max", 5),
        "min": opt_args.get("min", 1),
        "int": opt_args.get("int", True),
    }

    await botfunc.run_sql(
        """INSERT INTO vote (gid, uid, type, status, result, title, options) VALUES (%s, %s, 3, false, -1, %s, %s);""",
        (group.id, member.id, main_args["title"], json.dumps(options, ensure_ascii=False)),
    )
    results = await botfunc.select_fetchone(
        GET_MAX_ID
    )

    opt_str = "\n".join([f"{x[0]}.{x[1]}" for x in enumerate(options["options"].keys(), 1)])
    send_msg = (
        f"⟨{results[0]}⟩ 号表决已创建！内容如下：\n"
        f"类型：评分投票\n"
        f"发起者：{member.id}\n"
        f"仅可参加：{options['accept']}\n"
        f"不可参加：{options['deny']}\n"
        f"可选最高分：{options['max']}\n"
        f"可选最低分：{options['min']}\n"
        f"必须为整数：{options['int']}\n"
        f"标题：{main_args['title']}\n"
        f"选项：\n"
        f"{opt_str}"
    )
    await app.send_group_message(group, send_msg)


@channel.use(AlconnaSchema(AlconnaDispatcher(problem.sort, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    opt_args = result.other_args
    options = {
        "options": {key: 0 for key in main_args["option"]},
        "deny": opt_args.get("deny", []),
        "accept": opt_args.get("accept", [])
    }

    await botfunc.run_sql(
        """INSERT INTO vote (gid, uid, type, status, result, title, options) VALUES (%s, %s, 4, false, -1, %s, %s);""",
        (group.id, member.id, main_args["title"], json.dumps(options, ensure_ascii=False)),
    )
    results = await botfunc.select_fetchone(
        GET_MAX_ID
    )

    opt_str = "\n".join([f"{x[0]}.{x[1]}" for x in enumerate(options["options"].keys(), 1)])
    send_msg = (
        f"⟨{results[0]}⟩ 号表决已创建！内容如下：\n"
        f"类型：排序投票\n"
        f"发起者：{member.id}\n"
        f"仅可参加：{options['accept']}\n"
        f"不可参加：{options['deny']}\n"
        f"标题：{main_args['title']}\n"
        f"选项：\n"
        f"{opt_str}"
    )
    await app.send_group_message(group, send_msg)


@channel.use(AlconnaSchema(AlconnaDispatcher(answer.single, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    ...  # TODO


@channel.use(AlconnaSchema(AlconnaDispatcher(answer.single, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    ...  # TODO


@channel.use(AlconnaSchema(AlconnaDispatcher(answer.multiple, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    ...  # TODO


@channel.use(AlconnaSchema(AlconnaDispatcher(answer.proportion, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    ...  # TODO


@channel.use(AlconnaSchema(AlconnaDispatcher(answer.score, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    ...  # TODO


@channel.use(AlconnaSchema(AlconnaDispatcher(answer.sort, skip_for_unmatch=False)))
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def initiate_sort(
        app: Ariadne,
        group: Group,
        member: Member,
        result: Arparma
):
    logger.debug(result)
    main_args = result.main_args
    ...  # TODO
