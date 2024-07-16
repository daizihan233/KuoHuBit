#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
"""
简单多数制

相对于比例代表制，亦是三权分立体制中议会选举中分配议席的方法之一，因此又称多数代表制（英语：Majoritarian Representation）。

本程序采用“相对多数制”而非“绝对多数制”

即在投票时，得票数最多的候选人或候选人组合当选。
"""


async def pvs(mapping: dict, votes: list) -> tuple:
    """
    简单多数制的计算函数
    :param mapping: 选项序号与候选选项的映射
    :param votes: 投票数据
    :return: 计算得到的结果、原始数据与计算步骤
    """
    steps = []
    raw_result = {c: 0 for c in mapping.values()}
    for i in votes:
        if isinstance(i, list):
            for j in i:
                steps.append(f"从选票 {i} 中获取 {mapping[j]}，查询对应到 {mapping[j]} 并增加 1 票")
                raw_result[mapping[j]] += 1
        elif isinstance(i, int):
            steps.append(f"选票中 {i} 查询对应到 {mapping[i]} 并增加 1 票")
            raw_result[mapping[i]] += 1
    results = sorted(raw_result.items(), key=lambda x: x[1], reverse=True)
    return results, raw_result, steps
