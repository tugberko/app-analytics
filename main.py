import dotenv
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

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

def get_client_ip(request: Request):

    forwarded = request.headers.get("x-real-ip")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.client.host

app = FastAPI()

limiter = Limiter(key_func=get_client_ip)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.add_middleware(SlowAPIMiddleware)





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
@limiter.limit("5/15minutes")
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

    print(request.headers)
    print(request.client.host)

    response = await MeHandler().handle(request)

    return response


@app.get("/")
async def root():
    return "Hello"
