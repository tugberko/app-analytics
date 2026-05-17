import dotenv
from fastapi import FastAPI, Request

from starlette.responses import JSONResponse

from handlers.backup_handler import BackupHandler
from handlers.heartbeat_handler import HeartbeatHandler
from handlers.me_handler import MeHandler

from handlers.otp_request_handler import OTPRequestHandler
from handlers.otp_verification_handler import OTPVerificationHandler
from handlers.restore_handler import RestoreHandler

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
        "key": "value"
    }

    return JSONResponse(status_code=200, content=config)


@app.post("/practivo/request-otp")
async def request_otp(request: Request):
    response = await OTPRequestHandler().handle(request)

    return response

@app.post("/practivo/verify-otp")
async def verify_otp(request: Request):
    response = await OTPVerificationHandler().handle(request)

    return response


@app.post("/practivo/backup")
async def backup(request: Request):
    response = await BackupHandler().handle(request)

    return response

@app.post("/practivo/restore")
async def restore(request: Request):
    response = await RestoreHandler().handle(request)

    return response

@app.post("/practivo/me")
async def me(request: Request):
    response = await MeHandler().handle(request)

    return response


@app.get("/")
async def root():
    return "Hello"
