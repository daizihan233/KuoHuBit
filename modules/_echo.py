#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()
channel.name("echo")
channel.description("echo 第一个输出")
channel.author("HanTools")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def echo(app: Ariadne, group: Group, message: MessageChain):
    if message.display.startswith("/echo "):
        await app.send_message(
            group,
            MessageChain(f"{message.display[6:]}"),
        )
