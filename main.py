import os

import dotenv
from fastapi import FastAPI, Request
from starlette.middleware.errors import JS
from starlette.responses import JSONResponse

from database_connection import MySQLClient
from handlers.heartbeat_handler import HeartbeatHandler

dotenv.load_dotenv(
    ".env",
    override=True,
)

app = FastAPI()

@app.post("/practivo/heartbeat")
async def handle_heartbeat(request: Request):
    print("Request received")
    print(await request.json())

    return await HeartbeatHandler().handle_heartbeat(request)

@app.get("/practivo/config")
async def get_config(request: Request):

    config = {
        "key" : "value"
    }

    return JSONResponse(status_code=200, content=config)

@app.get("/")
async def root():
    return "Hello"


