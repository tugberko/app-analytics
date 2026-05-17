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

        pass

    async def find_user_by_email(self, email: str) -> Optional[int]:
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