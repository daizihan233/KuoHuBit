import uvicorn
from fastapi import FastAPI, Response, Body

import botfunc

app = FastAPI()


@app.get("/bot/data/get/six")
async def six(response: Response):
    response.status_code = 200
    data = await botfunc.select_fetchall(
        "SELECT uid, count FROM six ORDER BY count DESC "
    )
    return {"status": 200, "data": data}


@app.post("/bot/imgsafe/fix")
def fix_result(
        response: Response,
        request_id=Body("RequestId")
):
    response.status_code = 200
    botfunc.r.hdel("imgsafe", botfunc.r.hget("imgsafe", request_id))
    botfunc.r.hdel("imgsafe", request_id)
    return {"status": 200}

if __name__ == "__main__":
    uvicorn.run("botapi:app", port=8989, host="0.0.0.0", reload=True)
