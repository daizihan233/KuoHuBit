"""
KHB 常用的逻辑判断
"""
from graia.amnesia.message import MessageChain
from graia.ariadne import Ariadne
from graia.ariadne.message.element import At, Plain, Image
from graia.ariadne.model import Group, Member, MemberPerm, Friend
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop

import botfunc


def check_authority_bot_op(prompt: bool = True):
    """
    检查权限是否是机器人的op
    :return: Depend
    """

    async def check_authority(app: Ariadne, group: Group, member: Member):
        admin = await botfunc.get_all_admin()
        if member.id not in admin:
            if prompt:
                await app.send_message(
                    group,
                    MessageChain(
                        [
                            At(member.id),
                            Plain("你没有指定权限，无法执行此指令\n"),
                            Plain("要求：【是】机器人的op")
                        ]
                    )
                )
            raise ExecutionStop

    return Depend(check_authority)


def check_authority_group_op(prompt: bool = True):
    """
    检查权限是否是群管理员/群主
    :return: Depend
    """

    async def check_authority(app: Ariadne, group: Group, member: Member):
        if member.permission not in [MemberPerm.Administrator, MemberPerm.Owner]:
            if prompt:
                await app.send_message(
                    group,
                    MessageChain(
                        [
                            At(member.id),
                            Plain("你没有指定权限，无法执行此指令\n"),
                            Plain("要求：【是】群管理员 / 【是】群主")
                        ]
                    )
                )
            raise ExecutionStop

    return Depend(check_authority)


def check_authority_op(prompt: bool = True):
    """
    检查权限是否是群管理员/群主/机器人op
    :return: Depend
    """

    async def check_authority(app: Ariadne, group: Group, member: Member):
        admin = await botfunc.get_all_admin()
        if member.permission not in [MemberPerm.Administrator, MemberPerm.Owner] and member.id not in admin:
            if prompt:
                await app.send_message(
                    group,
                    MessageChain(
                        [
                            At(member.id),
                            Plain("你没有指定权限，无法执行此指令\n"),
                            Plain("要求：【是】群管理员 / 【是】群主 / 【是】机器人op")
                        ]
                    )
                )
            raise ExecutionStop

    return Depend(check_authority)


def check_authority_su():
    """
    检查权限是否是机器人主人
    :return: Depend
    """

    async def check_authority(member: Member):
        su = await botfunc.get_su()
        if member.id != su:
            raise ExecutionStop

    return Depend(check_authority)


def check_friend_su():
    """
    检查好友是否是机器人主人
    :return: Depend
    """

    async def check_authority(friend: Friend):
        su = await botfunc.get_su()
        if friend.id != su:
            raise ExecutionStop

    return Depend(check_authority)


def check_authority_black(prompt: bool = True):
    """
    检查权限是否是黑名单内的人
    :return: Depend
    """

    async def check_authority(app: Ariadne, group: Group, member: Member):
        sb = await botfunc.get_all_sb()
        if member.id not in sb:
            if prompt:
                await app.send_message(
                    group,
                    MessageChain(
                        [
                            At(member.id),
                            Plain("你没有指定权限，无法执行此指令\n"),
                            Plain("最低要求：【是】黑名单内的人")
                        ]
                    )
                )
            raise ExecutionStop

    return Depend(check_authority)


def check_authority_not_black(prompt: bool = True):
    """
    检查权限是否是黑名单内的人
    :return: Depend
    """

    async def check_authority(app: Ariadne, group: Group, member: Member):
        sb = await botfunc.get_all_sb()
        if member.id in sb:
            if prompt:
                await app.send_message(
                    group,
                    MessageChain(
                        [
                            At(member.id),
                            Plain("你没有指定权限，无法执行此指令\n"),
                            Plain("最低要求：【不是】黑名单内的人")
                        ]
                    )
                )
            raise ExecutionStop

    return Depend(check_authority)


def check_authority_member():
    """
    检查权限是否是群成员
    :return: Depend
    """

    async def check_authority(member: Member):
        if member.permission != MemberPerm.Member:
            raise ExecutionStop

    return Depend(check_authority)


def match_image():
    """
    检测是否含有图片
    :return: Depend
    """

    async def check_message(message: MessageChain):
        if Image not in message:
            raise ExecutionStop

    return Depend(check_message)


def match_text():
    """
    检测是否含有文本
    :return: Depend
    """

    async def check_message(message: MessageChain):
        if Plain not in message:
            raise ExecutionStop

    return Depend(check_message)
