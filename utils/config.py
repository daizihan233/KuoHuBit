#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import yaml
from loguru import logger

from utils.var import config_yaml, cloud_config_json


def get_config(name: str):
    try:
        return config_yaml[name]
    except KeyError:
        logger.error(f"{name} 在配置文件中找不到")
        return None


def get_cloud_config(name: str):
    try:
        return cloud_config_json[name]
    except KeyError:
        logger.error(f"{name} 在配置文件中找不到")
        return ""


def get_dyn_config(name: str):
    dyn_yaml = yaml.safe_load(open("dynamic_config.yaml", "r", encoding="UTF-8"))
    try:
        return dyn_yaml[name]
    except KeyError:
        logger.error(f"{name} 在配置文件中找不到")
        return []
