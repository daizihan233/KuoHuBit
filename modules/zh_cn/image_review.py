import base64
import hashlib
import json

import yaml
from graia.amnesia.message import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.exception import TencentCloudSDKException
from tencentcloud.ims.v20201229 import ims_client, models

import botfunc
import depen

channel = Channel.current()
channel.name("图片审核")
channel.description("你疑似有点太极端了")
channel.author("HanTools")
dyn_config = 'dynamic_config.yaml'


async def using_tencent_cloud(content: str, user_id) -> dict:
    if botfunc.r.hexists("imgsafe", hashlib.sha384(content.encode()).hexdigest()):
        return json.loads(botfunc.r.hget("imgsafe", hashlib.sha384(content.encode()).hexdigest()))
    try:
        cred = credential.Credential(
            botfunc.get_cloud_config("QCloud_Secret_id"),
            botfunc.get_cloud_config("QCloud_Secret_key")
        )
        client = ims_client.ImsClient(cred, botfunc.get_config("Region"))
        req = models.ImageModerationRequest()
        params = {
            "FileContent": content,  # base64
            "User": {
                "UserId": user_id,
                "AccountType": 2
            }
        }
        req.from_json_string(json.dumps(params))
        resp = client.ImageModeration(req)
        logger.info(resp.to_json_string())
        botfunc.r.hset(
            'imgsafe', hashlib.sha384(content.encode()).hexdigest(),
            json.dumps(
                {
                    "Suggestion": resp.Suggestion,
                    "SubLabel": resp.SubLabel,
                    "DataId": resp.DataId
                }
            )
        )
        logger.debug(f"新图片入库！{resp.Suggestion} | {resp.SubLabel} | {resp.DataId}")
        return {
            "Suggestion": resp.Suggestion,
            "SubLabel": resp.SubLabel,
            "DataId": resp.DataId
        }
    except TencentCloudSDKException as err:
        logger.error(err)
    return {
        "Suggestion": "Pass",
        "SubLabel": "",
        "DataId": ""
    }


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            MatchContent("图片审核，启动！"),
            depen.check_authority_op()
        ]
    )
)
async def start_word(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    cfy['img'].append(group.id)
    cfy['img'] = list(set(cfy["img"]))
    with open(dyn_config, 'w') as cf:
        yaml.dump(cfy, cf)
    await app.send_message(group, MessageChain([At(event.sender.id), Plain(" OK辣！")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            MatchContent("图片审核，卸载！"),
            depen.check_authority_op()
        ]
    )
)
async def stop_word(app: Ariadne, group: Group, event: GroupMessage):
    with open(dyn_config, 'r') as cf:
        cfy = yaml.safe_load(cf)
    try:
        cfy['img'].remove(group.id)
        cfy['img'] = list(set(cfy["img"]))
        with open(dyn_config, 'w') as cf:
            yaml.dump(cfy, cf)
        await app.send_message(group, MessageChain([At(event.sender.id), Plain(" OK辣！")]))
    except Exception as err:
        await app.send_message(group, MessageChain([At(event.sender.id), Plain(f" 报错辣！{err}")]))


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[depen.match_image()]
    )
)
async def image_review(app: Ariadne, message: MessageChain, event: GroupMessage):
    if event.sender.id in botfunc.get_dyn_config("img"):
        for i in message[Image]:
            result = await using_tencent_cloud(base64.b64encode(i.get_bytes()).decode(), event.sender.id)
            logger.debug(result)
            if result['Suggestion'] == "Block":
                await app.recall_message(event.source, event.sender.group)
                await app.send_message(
                    event.sender.group,
                    MessageChain([At(event.sender.id), Plain(
                        " 你疑似有点太极端了\n"
                        f"识别标签：{result['SubLabel']}\n"
                        f"数据编码：{result['DataId']}\n"
                        f"\n"
                        f"**当你认为这是误判请提供【数据编码】给机器人账号所有者**\n"
                        f"【数据来源：腾讯云图片内容安全】"
                    )])
                )
