import pkgutil

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya import Saya

import botfunc

saya = create(Saya)

app = Ariadne(
    connection=config(
        botfunc.get_config('qq'),
        botfunc.get_config('verifyKey'),
        HttpClientConfig(host="http://localhost:8088"),
        WebsocketClientConfig(host="http://localhost:8088"),
    ),
)


with saya.module_context():
    for module_info in pkgutil.iter_modules(["modules"]):
        if module_info.name.startswith("_"):
            # 假设模组是以 `_` 开头的，就不去导入
            # 根据 Python 标准，这类模组算是私有函数
            continue
        saya.require(f"modules.{module_info.name}")
for module, channel in saya.channels.items():
    print(
        f"module: {module}\n"
        f"name: {channel.meta['name']}\n"
        f"author: {' '.join(channel.meta['author'])}\n"
        f"description: {channel.meta['description']}"
    )

app.launch_blocking()

