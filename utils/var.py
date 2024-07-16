import json
import pathlib
import sys

import yaml
from loguru import logger

from utils.file import safe_file_write

sensitive_words = []
no_6 = []
inm = []
cue = {}
cue_status = {}
cue_who = {}

try:
    config_yaml = yaml.load(open('config.yaml', encoding='UTF-8'), Loader=yaml.FullLoader)
except FileNotFoundError:
    safe_file_write('config.yaml', """qq: 114514  # 运行时登录的 QQ 号
su: 1919810  # 机器人主人的 QQ 号
verifyKey: ""  # MAH 的 verifyKey
recall: 30  # 涩图撤回等待时长（单位：秒）
# 如果你没有那么多涩图API可以填一样的URL
setu_api: "https://api.jiecs.top/lolicon?r18=2"  # 涩图 API
setu_api2: "https://www.acy.moe/api/r18"  # 涩图 API 2
setu_api2_probability: 5  # 表示【涩图 API 2】的被调用的概率为 1/n
NewFriendRequestEvent: true  # 是否自动通过好友添加：true -> 自动通过 | false -> 自动拒绝
BotInvitedJoinGroupRequestEvent: true  # 是否自动通过加群邀请：同上
mirai_api_http: "http://localhost:8080"  # 连接到 MAH 的地址
count_ban: 4  # 木鱼调用频率限制
# 注意：腾讯云内容安全 API 收费为 0.0025/条
text_review: false  # 是否使用腾讯云内容安全 API 对文本内容进行审核：true -> 是 | false -> 否，使用本地敏感词库
violation_text_review: true  # 是否使用腾讯云内容安全 API 对[违规]文本内容进行复审：true -> 是 | false -> 否，使用本地敏感词库""")
    logger.error(
        'config.yaml 文件不存在，已生成默认配置文件，请修改后重新运行。'
    )
    sys.exit(1)

try:
    cloud_config_json = json.load(open("cloud.json", "r", encoding="UTF-8"))
except FileNotFoundError:
    safe_file_write(
        "cloud.json",
        """{
  "QCloud_Secret_id": "",
  "QCloud_Secret_key": "",
  "MySQL_Pwd": "",
  "MySQL_Port": 3306,
  "MySQL_Host": "localhost",
  "MySQL_db": "database",
  "MySQL_User": "root",
  "Redis_Host": "localhost",
  "Redis_port": 6379,
  "snao_key": "",
  "gptkey": "AIGC10241-"
}""",
    )
    logger.error(
        "cloud.json 未创建，程序已自动创建，请参考 https://github.com/daizihan233/KuoHuBit/issues/17 填写该文件的内容"
    )
    sys.exit(1)
if not pathlib.Path("./dynamic_config.yaml").exists():
    safe_file_write(
        "dynamic_config.yaml",
        """mute: []
word: []
img: []""",
    )
    logger.warning("dynamic_config.yaml 已被程序自动创建")
