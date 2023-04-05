import datetime

import ntplib
import pytz
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.util.saya import listen, decorate
from graia.saya import Channel

channel = Channel.current()
channel.name("异世界 - 时间查询")
channel.description("呃？这是哪？")
channel.author("OW-KH")


@listen(GroupMessage)
@decorate(MatchContent("异世界时间"))
async def timer(app: Ariadne, event: GroupMessage):
    if event.sender.group != 673460010:
        return
    ntp = ntplib.NTPClient()
    utc = datetime.datetime.now(tz=pytz.UTC)
    utc_8 = datetime.datetime.now()
    try:
        owst = datetime.datetime.utcfromtimestamp(ntp.request("owst.khbit.cn").tx_time)
    except TimeoutError:
        owst = 'TimeOut - owst.khbit.cn'
    try:
        owct = datetime.datetime.utcfromtimestamp(ntp.request("owst.khbit.cn").tx_time)
    except TimeoutError:
        owct = 'TimeOut - owct.khbit.cn'
    await app.send_message(
        target=event.sender.group,
        quote=event.source,
        message=f"OWST : {owst}\n"
                f"OWCT : {owct}\n"
                f"UTC  : {utc}\n"
                f"UTC+8: {utc_8}"
    )
