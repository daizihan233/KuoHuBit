import fcntl
import json

import requests_cache
import yaml
from loguru import logger

config_yaml = yaml.safe_load(open('config.yaml', 'r', encoding='UTF-8'))
cloud_config_json = json.load(open('cloud.json', 'r', encoding='UTF-8'))
dyn_yaml = yaml.safe_load(open('dynamic_config.yaml', 'r', encoding='UTF-8'))


def _rat(log, des, v):
    """
    输出日志并返回指定值
    :param log: 使用什么等级输出日志，传入一个函数
    :param des: 描述，必须含有 %s 以拼接字符串
    :param v: 需要返回的值
    :return: 参数中的v
    """
    log(des % v)
    return v


def get_config(name: str):
    try:
        return _rat(logger.debug, f"{name} -> %s", config_yaml[name])
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def get_cloud_config(name: str):
    try:
        return _rat(logger.debug, f"{name} -> %s", cloud_config_json[name])
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
        return None


def get_dyn_config(name: str):
    try:
        return _rat(logger.debug, f"{name} -> %s", dyn_yaml[name])
    except KeyError:
        logger.error(f'{name} 在配置文件中找不到')
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


backend = requests_cache.RedisCache(host=get_cloud_config('Redis_Host'), port=get_cloud_config('Redis_port'))
session = requests_cache.CachedSession("global_session", backend=backend, expire_after=360)
