import hashlib
from typing import Optional

from starlette.responses import JSONResponse
from fastapi import Request

from utils.database_connection import MySQLClient


class MeHandler:

    def __init__(self):

        self.db = MySQLClient()

        self.raw_token: str = ""
        self.hashed_token: str = ""

        self.user_id: Optional[int] = None

        self.most_recent_backup: Optional[str] = None

    async def find_user_id(self):

        record = await self.db.fetch_one(
            query = "SELECT * FROM tokens WHERE token_hash = %s",
            params=(self.hashed_token,)
        )

        self.user_id = record["user_id"]


    async def get_most_recent_backup(self):

        record = await self.db.fetch_one(
            query = """
                SELECT * FROM backups WHERE user_id = %s ORDER BY created_at DESC LIMIT 1
            """,
            params=(self.user_id,)
        )

        print(record)

        self.most_recent_backup = record["created_at"]


    async def handle(self, request: Request) -> JSONResponse:

        payload = await request.json()

        self.raw_token = payload["token"]
        self.hashed_token = hashlib.sha256(self.raw_token.encode()).hexdigest()

        await self.get_most_recent_backup()

        return JSONResponse(status_code=200, content={"most_recent_backup": self.most_recent_backup})

