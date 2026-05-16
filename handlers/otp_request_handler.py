import hashlib
import os
import secrets

import aiohttp
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from utils.database_connection import MySQLClient
from utils.email_validator import EmailValidator


class OTPRequestHandler:

    SUCCESS_RESPONSE = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True}
        )

    FAILURE_RESPONSE = JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"success": False}
        )

    EMAIL_SERVICE_URL = "https://api.mailjet.com/v3.1/send"

    def __init__(self):
        self.db = MySQLClient()

        self.email: str = ""
        self.otp: str = ""
        self.hashed_otp: str = ""

    def generate_otp(self):
        self.otp = str(secrets.randbelow(900000) + 100000)

        self.hashed_otp = hashlib.sha256(self.otp.encode()).hexdigest()

    async def insert_otp(self):

        self.generate_otp()

        # Delete old OTPs
        await self.db.execute(
            query="""
                DELETE FROM email_otps
                WHERE email = %s;
            """,
            params=(self.email,)
        )

        # Create new OTP
        result = await self.db.insert_and_get_id(
            query= """
                INSERT INTO email_otps (
                    email,
                    otp_hash
                )
                VALUES (
                    %s,
                    %s,
                );
            """,
            params=(self.email, self.hashed_otp)
        )

        print(result)

    async def send_email(self):

        auth = aiohttp.BasicAuth(
            os.getenv("MAILJET_API_KEY"),
            os.getenv("MAILJET_SECRET_KEY"),
        )

        payload = {
            "Messages": [
                {
                    "From": {
                        "Email": "repertoire-upkeep@tugberk.cloud",
                        "Name": "Repertoire Upkeep"
                    },
                    "To": [
                        {
                            "Email": self.email,
                            "Name": self.email
                        }
                    ],
                    "Subject": "Repertoire Upkeep Security Code",
                    "TextPart": f"Greetings, your code is {self.otp}",
                    "HTMLPart": f"Greetings, your code is {self.otp}"
                }
            ]
        }

        async with aiohttp.ClientSession(auth=auth) as session:
            async with session.post(self.EMAIL_SERVICE_URL, json=payload) as resp:
                status = resp.status
                data = await resp.json()

                print("Status:", status)
                print("Response:", data)

                if status >= 400:
                    raise Exception(f"Mailjet error {status}: {data}")


    async def handle(self, request: Request) -> JSONResponse:
        payload = await request.json()

        try:
            self.email = payload["email"].strip().lower()
        except (KeyError, AttributeError) as e:
            print(e)
            return self.FAILURE_RESPONSE

        is_email_valid = await EmailValidator().check_if_valid_email(self.email)
        if not is_email_valid:
            return self.FAILURE_RESPONSE

        try:
            await self.insert_otp()
            await self.send_email()
        except Exception as e:
            print(e)
            return self.FAILURE_RESPONSE

        return self.SUCCESS_RESPONSE