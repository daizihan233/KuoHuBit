"""
注意：本插件偏定制性，不会在配置文件中给予相关配置
若要禁用此插件，请将文件名改为 _imgsafe.py
"""
#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import graia.ariadne.message.chain
import imagehash
import redis
import requests
from PIL import Image
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Member, MemberPerm
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

import botfunc

channel = Channel.current()
channel.name("图片内容安全")
channel.description("调用腾讯云API检测图片并撤回")
channel.author("HanTools")


def check_group(*groups: int):
    async def check_group_deco(group: Group):
        if group.id not in groups:
            raise ExecutionStop

    return Depend(check_group_deco)


def check_member():
    async def check_member_deco(member: Member):
        if member.permission != MemberPerm.Member:
            raise ExecutionStop

    return Depend(check_member_deco)


def tencent_image_api(img_base, biz, user_info):
    import json
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.ims.v20201229 import ims_client, models
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey,此处还需注意密钥对的保密
        # 密钥可前往https://console.cloud.tencent.com/cam/capi网站进行获取
        cred = credential.Credential(secret_id=botfunc.get_cloud_config('QCloud_Secret_id'),
                                     secret_key=botfunc.get_cloud_config('QCloud_Secret_id'))
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        http_profile = HttpProfile()
        http_profile.endpoint = "ims.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = ims_client.ImsClient(cred, "ap-beijing", client_profile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.ImageModerationRequest()
        params = {
            "BizType": biz,
            "FileContent": img_base,
            "User": user_info
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ImageModerationResponse的实例，与请求对象对应
        resp = client.ImageModeration(req)
        # 输出json格式的字符串回包
        t = json.loads(resp.to_json_string())
        return t['Suggestion'], t['Label'], t['RequestId']
    except TencentCloudSDKException as err:
        print(err)
        return 'Pass'


def img_safe(msg, biz, gid, uid):
    mlist = []
    for i in msg:
        mlist.append(i)
    for im in mlist:
        if int(requests.head(im.url, allow_redirects=True).headers.get('Content-Length')) < 5 * 1048576:
            botfunc.safe_file_write('tmp114.png', requests.get(im.url).content, 'wb')
            dh = str(imagehash.dhash(Image.open('tmp114.png')))
            # 检查Redis中是否存在该图片的hash值
            p = redis.ConnectionPool(host='43.155.59.113', port=6009, decode_responses=True)
            r = redis.Redis(connection_pool=p)
            if r.hexists('imh', dh):
                dhu = r.hget('imh', dh)
                dhu = dhu.split(',')
                ta = (dhu[0], "(From Redis, it's UNKNOWN)", dhu[1])
            else:
                ta = tencent_image_api(im.base64,
                                       biz,
                                       {
                                           "UserId": str(uid),
                                           "AccountType": "2"
                                       }
                                       )
                r.hset('imh', dh, f'{ta[0]},{ta[2]},{im.url},{gid}')
                r.hset('imh', ta[2], f'{dh}')
            if ta[0] == 'Block':  # 确定
                return "Block"
            elif ta[0] == 'Review':  # 疑似
                return "Review"


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[
            check_group(971741566),
            check_member()
        ],
    )
)
async def check_img(message: MessageChain, event: GroupMessage):
    res = img_safe(msg=message[graia.ariadne.message.chain.Image], biz='htv1', gid=event.sender.group.id,
                   uid=event.sender.id)
    return res
