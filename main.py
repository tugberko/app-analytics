import dotenv

from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse

from handlers.backup_handler import BackupHandler
from handlers.heartbeat_handler import HeartbeatHandler
from handlers.me_handler import MeHandler
from handlers.otp_request_handler import OTPRequestHandler
from handlers.otp_verification_handler import OTPVerificationHandler
from handlers.restore_handler import RestoreHandler

dotenv.load_dotenv(".env", override=True)



def get_client_ip(request: Request) -> str:
    """
    This function extracts the client ip from the request.
    :param request: Name says it all
    :return: IP address of the client
    """

    x_real_ip = request.headers.get("x-real-ip")
    if x_real_ip:
        return x_real_ip.strip()

    x_forwarded = request.headers.get("x-forwarded-for")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()

    if request.client:
        return request.client.host

    return "unknown"


# -------------------------
# App + Limiter
# -------------------------
app = FastAPI()

limiter = Limiter(key_func=get_client_ip)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# -------------------------
# Silent rate limit handler
# -------------------------
async def silent_rate_limit_handler(request: Request, exc: RateLimitExceeded):

    print("Dropping due to rate limit, however will return 200 OK.")

    return JSONResponse(
        status_code=200,
        content={"success": True}
    )


app.add_exception_handler(
    RateLimitExceeded,
    silent_rate_limit_handler
)


# -------------------------
# Routes
# -------------------------
@app.post("/practivo/heartbeat")
async def handle_heartbeat(request: Request):
    return await HeartbeatHandler().handle_heartbeat(request)


@app.get("/practivo/config")
async def get_config():
    return {"key": "value"}


@app.post("/practivo/request-otp")
@limiter.limit("5/15minutes")
async def request_otp(request: Request):
    return await OTPRequestHandler().handle(request)


@app.post("/practivo/verify-otp")
@limiter.limit("4/1minutes")
async def verify_otp(request: Request):
    return await OTPVerificationHandler().handle(request)


@app.post("/practivo/backup")
async def backup(request: Request):
    return await BackupHandler().handle(request)


@app.post("/practivo/restore")
async def restore(request: Request):
    return await RestoreHandler().handle(request)


@app.post("/practivo/me")
async def me(request: Request):
    return await MeHandler().handle(request)


@app.get("/")
async def root():
    return "Hello"