from fastapi.responses import JSONResponse
from fastapi import Request
from starlette import status

from services.otp_service import OTPService
from utils.email_validator import EmailValidator


class OTPRequestHandler:

    RESPONSE = JSONResponse(status_code=status.HTTP_200_OK, content={"error": None})

    def __init__(self) -> None:
        pass

    def check_if_payload_valid(self, payload: dict) -> bool:

        if any([
            "email" not in payload,
        ]):
            return False

        return True


    async def handle(self, request: Request) -> JSONResponse:

        otp_service = OTPService()

        payload = await request.json()

        is_payload_valid = self.check_if_payload_valid(payload)
        if not is_payload_valid:
            print("Invalid payload")
            return self.RESPONSE

        email = payload["email"].lower().strip()

        is_email_valid = await EmailValidator().check_if_valid_email(email)
        if not is_email_valid:
            print("Invalid email")
            return self.RESPONSE

        if await otp_service.check_if_otp_requested_too_frequently_recently(email):
            return JSONResponse(status_code=status.HTTP_200_OK, content={"error": "Yavaş biraz"})

        otp = otp_service.generate_otp()
        await otp_service.insert_otp_email_pair_into_db(email=email, otp=otp)

        await otp_service.display_otp(otp)

        return self.RESPONSE