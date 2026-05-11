from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/heartbeat")
async def heartbeat(request: Request):
    body = await request.json()
    print(body)
    return {"status": "ok"}

@app.get("/")
async def root():
    return "Hello"