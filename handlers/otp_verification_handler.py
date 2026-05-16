import hashlib

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from utils.database_connection import MySQLClient


class OTPVerificationHandler:
    FAILURE_RESPONSE = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False}
    )

    def __init__(self):
        self.db = MySQLClient()

        self.email: str = ""
        self.otp: str = ""
        self.hashed_otp: str = ""

    async def mark_as_used(self, email_otp_id: int):
        result = await self.db.execute(
            query="""
                  UPDATE email_otps
                  SET is_used = TRUE
                  WHERE id = %s;

                  """,
            params=(email_otp_id,)
        )

        print(result)

    async def check_if_otp_good(self) -> bool:
        record = await self.db.fetch_one(
            query="""
                  SELECT *
                  FROM email_otps EO
                  WHERE EO.email = %s
                    AND EO.otp_hash = %s
                    AND CURDATE() < EO.expires_at
                    AND EO.is_used = FALSE
                  """,
            params=(self.email, self.hashed_otp)
        )

        if record is not None:
            await self.mark_as_used(record["id"])
            return True

        return False

    async def upsert_user(self) -> int:
        """
        This function upserts the users and returns the user id
        :return:
        """

        # If present
        record = await self.db.fetch_one(
            query="""
                  SELECT *
                  FROM users
                  WHERE email = %s LIMIT 1;
                  """,
            params=(self.email,)
        )

        if record is not None:
            return record["id"]

        # New user
        new_user_id = await self.db.insert_and_get_id(
            query="""
                  INSERT INTO users (email)
                  VALUES (%s);
                  """,
            params=(self.email,)
        )

        return new_user_id

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

        self.email = payload["email"]
        self.otp = payload["otp"]
        self.hashed_otp = hashlib.sha256(self.otp.encode()).hexdigest()

        is_valid_payload = self.check_if_valid_payload(payload)
        if not is_valid_payload:
            return self.FAILURE_RESPONSE

        is_good = await self.check_if_otp_good()
        if not is_good:
            return self.FAILURE_RESPONSE

        user_id = await self.upsert_user()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"success": True, "user_id": user_id}
        )
