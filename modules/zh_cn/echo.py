from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import DetectPrefix
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()
channel.name("echo")
channel.description("echo 第一个输出")
channel.author("HanTools")


@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def echo(app: Ariadne, group: Group, message: MessageChain = DetectPrefix("/echo ")):
    if str(message).startswith('/echo'):  # 防止注入
        pass  # 这里不需要进行提示，防止出现机器人反复提示的问题
    else:
        await app.send_message(
            group,
            message,
        )
