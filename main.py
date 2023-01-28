# 此项目遵循 Mirai 使用的 AGPL-3.0 协议仍然保持开源并继续使用 AGPL-3.0
# 如果您需要在此项目的基础上改动那么我强烈建议：
#  - 保持开源
#  - 使用 AGPL-3.0 协议
#  - 注明使用了 Mirai 并其源代码来自此仓库
import pkgutil

import pymysql
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya import Saya
from loguru import logger

import botfunc
import cache_var
import modules

saya = create(Saya)

app = Ariadne(
    connection=config(
        botfunc.get_config('qq'),
        botfunc.get_config('verifyKey'),
        HttpClientConfig(host=botfunc.get_config('mirai_api_http')),
        WebsocketClientConfig(host=botfunc.get_config('mirai_api_http')),
    ),
)

conn = pymysql.connect(host=botfunc.get_cloud_config('MySQL_Host'), port=botfunc.get_cloud_config('MySQL_Port'),
                       user='root',
                       password=botfunc.get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                       database=botfunc.get_cloud_config('MySQL_db'))
cursor = conn.cursor()
# 载入敏感词列表
cursor.execute('SELECT wd, count FROM wd')
cache_var.sensitive_words = [x[0] for x in cursor.fetchall()]
conn.close()
with saya.module_context():
    for module_info in pkgutil.walk_packages(modules.__path__, modules.__name__ + "."):
        if module_info.name.startswith("_"):
            logger.warning(f'modules.{module_info.name} 被跳过载入')
            # 假设模组是以 `_` 开头的，就不去导入
            # 根据 Python 标准，这类模组算是私有函数
            continue
        saya.require(f"modules.{module_info.name}")
        logger.info(f'modules.{module_info.name} 被载入')
for module, channel in saya.channels.items():
    logger.info(f"module: {module}")
    logger.info(f"name: {channel.meta['name']}")
    logger.info(f"author: {' '.join(channel.meta['author'])}")
    logger.info(f"description: {channel.meta['description']}")

logger.success('恭喜！启动成功，0Error，至少目前如此，也祝你以后如此')
app.launch_blocking()
