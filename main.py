from fastapi import FastAPI, Request

from database_connection import MySQLClient

app = FastAPI()

@app.post("/heartbeat")
async def heartbeat(request: Request):
    body = await request.json()
    print(body)
    return {"status": "ok"}

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