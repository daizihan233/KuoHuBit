import pkgutil

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

saya = create(Saya)

app = Ariadne(
    connection=config(
        botfunc.get_config('qq'),
        botfunc.get_config('verifyKey'),
        HttpClientConfig(host=botfunc.get_config('mirai_api_http')),
        WebsocketClientConfig(host=botfunc.get_config('mirai_api_http')),
    ),
)


with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
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
