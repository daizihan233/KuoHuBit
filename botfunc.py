#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot

import fcntl
import json

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


def get_cloud_config(name: str):
    try:
        return json.load(open('cloud.json', 'r', encoding='UTF-8'))[name]
    except KeyError:
        return None


def get_dyn_config(name: str):
    try:
        y = yaml.load(open('dynamic_config.yaml', 'r', encoding='UTF-8'), yaml.SafeLoader)
        return y[name]
    except KeyError:
        return None


def safe_file_read(filename: str, encode: str = "UTF-8", mode: str = "r") -> str or bytes:
    if mode == 'r':
        with open(filename, mode, encoding=encode) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            tmp = f.read()
        return tmp
    if mode == 'rb':
        with open(filename, mode) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            tmp = f.read()
        return tmp


def safe_file_write(filename: str, s, mode: str = "w", encode: str = "UTF-8"):
    if 'b' not in mode:
        with open(filename, mode, encoding=encode) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(s)
    else:
        with open(filename, mode) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.write(s)
