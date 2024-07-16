#  本项目遵守 AGPL-3.0 协议，项目地址：https://github.com/daizihan233/MiraiHanBot
import redis
import requests_cache

from utils.config import get_cloud_config

if get_cloud_config("Redis_Pwd") is not None:
    backend = requests_cache.RedisCache(
        host=get_cloud_config("Redis_Host"),
        port=get_cloud_config("Redis_port"),
        password=get_cloud_config("Redis_Pwd"),
    )
    p = redis.ConnectionPool(
        host=get_cloud_config("Redis_Host"),
        port=get_cloud_config("Redis_port"),
        password=get_cloud_config("Redis_Pwd"),
    )
else:
    backend = requests_cache.RedisCache(
        host=get_cloud_config("Redis_Host"), port=get_cloud_config("Redis_port")
    )
    p = redis.ConnectionPool(
        host=get_cloud_config("Redis_Host"), port=get_cloud_config("Redis_port")
    )
session = requests_cache.CachedSession(
    "global_session", backend=backend, expire_after=360
)
r = redis.Redis(connection_pool=p, decode_responses=True)
