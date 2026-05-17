import secrets
from typing import Optional

from utils.database_connection import MySQLClient
from utils.hash import digest


class TokenService:

    def __init__(self):
        self.db = MySQLClient()

    async def grant_token(self, user_id: int) -> str:

        raw_token = secrets.token_hex(32)
        hashed_token = digest(raw_token)

        await self.db.insert_and_get_id(
            query="""
                  INSERT INTO tokens (user_id,
                                      token_hash,
                                      expires_at)
                  VALUES (%s,
                          %s,
                          DATE_ADD(NOW(), INTERVAL 30 DAY));
                  """,
            params=(user_id, hashed_token)
        )

        return raw_token

    async def find_user(self, raw_token: str) -> Optional[int]:
        hashed_token = digest(raw_token)

        record = await self.db.fetch_one(
            query="SELECT * FROM tokens WHERE token_hash = %s LIMIT 1",
            params=(hashed_token,)
        )

        if record is not None:
            return record["user_id"]

        return None