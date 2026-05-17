import hashlib
import secrets
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from services import user_service
from services.otp_service import OTPService
from services.token_service import TokenService
from services.user_service import UserService
from utils.database_connection import MySQLClient


class OTPVerificationHandler:
    FAILURE_RESPONSE = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False}
    )

    def __init__(self):
        self.db = MySQLClient()

    def check_if_valid_payload(self, payload: dict) -> bool:
        if "email" not in payload.keys() or "otp" not in payload.keys():
            print("Invalid payload")
            return False

        if not isinstance(payload["email"], str):
            print("Invalid payload")
            return False

        if not isinstance(payload["otp"], str):
            print("Invalid payload")
            return False

        if len(payload["otp"]) != 6:
            print("Invalid payload")
            return False

        return True

    async def handle(self, request: Request) -> JSONResponse:
        payload = await request.json()

        is_valid_payload = self.check_if_valid_payload(payload)
        if not is_valid_payload:
            return self.FAILURE_RESPONSE

        otp_service = OTPService()
        user_service = UserService()
        token_service = TokenService()

        is_good = await otp_service.check_if_otp_good(
            email=payload["email"],
            otp=payload["otp"]
        )
        if not is_good:
            return self.FAILURE_RESPONSE

        user_id = await user_service.create_user(email=payload["email"])
        token = await token_service.grant_token(user_id=user_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "token": token}
        )
