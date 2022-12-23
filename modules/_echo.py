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
async def setu(app: Ariadne, group: Group, message: MessageChain):
    if message.display.startswith("/echo "):
        await app.send_message(
            group,
            MessageChain(f"{message.display[6:]}"),
        )
