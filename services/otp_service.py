import secrets
from typing import Optional

from utils.database_connection import MySQLClient
from utils.hash import digest


class OTPService:

    def __init__(self):
        self.db = MySQLClient()

    @staticmethod
    def generate_otp() -> str:
        print("OTP being generated")
        return str(secrets.randbelow(900000) + 100000)

    async def insert_otp_email_pair_into_db(self, email: str, otp: str):
        """
        This method is used to insert an email-otp pair into the database
        :param email:
        :param otp:
        :return:
        """

        otp_hash = digest(otp)

        await self.db.insert_and_get_id(
            query="INSERT INTO email_otps (email, otp_hash) VALUES (%s, %s)",
            params=(email, otp_hash)
        )

    async def mark_as_used(self, email_otp_id: str):

        await self.db.execute(
            query="UPDATE email_otps SET is_used = 1 WHERE id = %s",
            params=(email_otp_id,)
        )

    async def check_if_otp_good(self, email: str, otp: str) -> Optional[bool]:
        otp_hash = digest(otp)

        record = await self.db.fetch_one(
            query="SELECT * FROM email_otps WHERE email = %s AND otp_hash = %s AND is_used = 0 AND NOW() < expires_at",
            params=(email, otp_hash)
        )

        if record is not None:
            await self.mark_as_used(record["id"])
            return record["id"]

        return None


    async def check_if_otp_requested_too_frequently_recently(self, email: str) -> bool:

        COOLDOWN = 5 # minutes

        result = await self.db.fetch_one(
            query="SELECT COUNT(*) AS count FROM email_otps WHERE email = %s AND created_at > NOW() - INTERVAL %s MINUTE",
            params=(email, COOLDOWN)
        )

        if result["count"] > 3:
            return True

        return False

    async def display_otp(self, otp: str):
        """
        This method is used to display OTP (preferably via email)
        :param otp:
        :return:
        """

        print(f"OTP is {otp}")
