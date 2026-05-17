from typing import Optional

from utils.database_connection import MySQLClient


class UserService:

    def __init__(self):
        self.db = MySQLClient()

    async def create_user(self, email: str) -> int:
        """

        :param email:
        :return:
        """

        user_id = await self.db.insert_and_get_id(
            query="INSERT INTO users (email) VALUES (%s)",
            params=(email,)
        )

        return user_id

    async def find_user_id_by_email(self, email: str) -> Optional[int]:
        """

        :param email:
        :return:
        """

        record = await self.db.fetch_one(
            query="SELECT * FROM users WHERE email = %s LIMIT 1",
            params=(email,)
        )

        if record is not None:
            return record["id"]

        return None

    async def find_email_by_user_id(self, user_id: int) -> Optional[str]:
        record = await self.db.fetch_one(
            query="SELECT * FROM users WHERE id = %s LIMIT 1",
            params=(user_id,)
        )

        if record is not None:
            return record["email"]

        return None