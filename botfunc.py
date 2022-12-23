#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import requests_cache
import yaml

backend = requests_cache.RedisCache(host='127.0.0.1', port=6009)
session = requests_cache.CachedSession("global_session", backend=backend, expire_after=360)


def get_config(name: str):
    try:
        y = yaml.load(open('config.yaml', 'r', encoding='UTF-8'), yaml.SafeLoader)
        return y[name]
    except KeyError:
        return None
