# 此项目遵循 Mirai 使用的 AGPL-3.0 协议仍然保持开源并继续使用 AGPL-3.0
# 如果您需要在此项目的基础上改动那么我强烈建议：
#  - 保持开源
#  - 使用 AGPL-3.0 协议
#  - 注明使用了 Mirai 并其源代码来自此仓库
import os

import pymysql
from arclet.alconna.graia import AlconnaBehaviour
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya import Saya
from loguru import logger

from utils.config import get_config, get_cloud_config

saya = create(Saya)
create(AlconnaBehaviour)

app = Ariadne(
    connection=config(
        get_config("qq"),
        get_config("verifyKey"),
        HttpClientConfig(host=get_config("mirai_api_http")),
        WebsocketClientConfig(host=get_config("mirai_api_http")),
    ),
)
try:
    conn = pymysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
        database=get_cloud_config("MySQL_db"),
    )
    cursor = conn.cursor()
except pymysql.err.InternalError:
    conn = pymysql.connect(
        host=get_cloud_config("MySQL_Host"),
        port=get_cloud_config("MySQL_Port"),
        user=get_cloud_config("MySQL_User"),
        password=get_cloud_config("MySQL_Pwd"),
        charset="utf8mb4",
    )
    cursor = conn.cursor()
    cursor.execute(
        """create database if not exists %s""", (get_cloud_config("MySQL_db"),)
    )

conn.commit()
conn.close()

with saya.module_context():
    for root, dirs, files in os.walk("./modules", topdown=False):
        for name in files:
            module = (
                os.path.join(root, name)
                .replace("\\", ".")
                .replace("./", "")
                .replace("/", ".")
                .split(".")
            )
            if "__pycache__" in module:
                continue
            if module[1] == "NO_USE" or len(module) > 3:
                continue
            module = ".".join(module)[:-3]
            logger.info(f"{module} 将被载入")
            saya.require(module)

for module, channel in saya.channels.items():
    logger.info(f"module: {module}")
    logger.info(f"name: {channel.meta['name']}")
    logger.info(f"author: {' '.join(channel.meta['author'])}")
    logger.info(f"description: {channel.meta['description']}")

logger.success("恭喜！启动成功，0Error，至少目前如此，也祝你以后如此")
app.launch_blocking()
