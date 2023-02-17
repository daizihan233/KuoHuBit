import asyncio
import json

import aiomysql
import uvicorn
from fastapi import FastAPI, Response

cloud_config_json = json.load(open('cloud.json', 'r', encoding='UTF-8'))


def get_cloud_config(name: str):
    try:
        return cloud_config_json[name]
    except KeyError:
        return None


app = FastAPI()
loop = asyncio.get_event_loop()


async def run_sql(sql, arg):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    await cur.execute(sql, arg)
    await cur.execute("commit")
    await cur.close()
    conn.close()


async def select_fetchall(sql, arg=None):
    conn = await aiomysql.connect(host=get_cloud_config('MySQL_Host'),
                                  port=get_cloud_config('MySQL_Port'),
                                  user='root',
                                  password=get_cloud_config('MySQL_Pwd'), charset='utf8mb4',
                                  db=get_cloud_config('MySQL_db'), loop=loop)

    cur = await conn.cursor()
    if arg:
        await cur.execute(sql, arg)
    else:
        await cur.execute(sql)
    r = await cur.fetchall()
    await cur.close()
    conn.close()
    return r


@app.get("/bot/data/get/six")
async def six(response: Response):
    response.status_code = 200
    data = await select_fetchall("SELECT uid, count FROM six ORDER BY count DESC ")
    return {"status": 200, "data": data}


if __name__ == '__main__':
    uvicorn.run("botapi:app", port=8989, host='0.0.0.0', reload=True)
