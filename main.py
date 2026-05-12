import os

import dotenv
from fastapi import FastAPI, Request

from database_connection import MySQLClient
from handlers.heartbeat_handler import HeartbeatHandler

dotenv.load_dotenv(
    ".env",
    override=True,
)

app = FastAPI()

@app.post("/practivo/heartbeat")
async def handle_heartbeat(request: Request):

    return await HeartbeatHandler().handle(request)


@app.get("/")
async def root():
    return "Hello"

@app.get("/display_tables")
async def display_tables(request: Request):

    query = """
        SHOW TABLES
    """

    result = await MySQLClient().execute(query)

    print(result)

    return {
        "result" : str(result)
    }

@app.get("/show_env")
async def show_env(request: Request):
    for key, value in os.environ.items():
        print(f"{key}: {value}")
