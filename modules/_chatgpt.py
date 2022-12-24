#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import openai
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.parser.base import MentionMe
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("chatgpt")
channel.description("聊天~~~")
channel.author("HanTools")


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage]
    )
)
async def repeat_record(app: Ariadne, group: Group, message: MessageChain = MentionMe()):
    openai.api_key = botfunc.get_cloud_config('OpenAI_Key')
    # Use the GPT-3 model
    completion = openai.Completion.create(
        engine="text-davinci-002",
        prompt=str(message),
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5
    )
    # Print the generated text
    print(completion.choices[0].text)
    await app.send_message(group, MessageChain(completion.choices[0].text))
