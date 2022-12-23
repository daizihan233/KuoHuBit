from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()
channel.name("HelloWorld")
channel.description("HelloWorld 创造世界")
channel.author("HanTools")



@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def hello(app: Ariadne, group: Group, message: MessageChain):
    if message.display == "你好":
         await app.send_message(
            group,
            MessageChain("HelloWorld!"),
         )

