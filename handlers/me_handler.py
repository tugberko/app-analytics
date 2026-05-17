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
        self.user_email: Optional[str] = None

        self.most_recent_backup: Optional[str] = None

    async def fetch_user_information(self):
        record = await self.db.fetch_one(
            query="""
                  SELECT * 
                  FROM tokens T
                      LEFT JOIN users U ON T.user_id = U.id
                  WHERE token_hash = %s AND CURDATE() < T.expires_at AND T.revoked_at IS NULL
                  """,
            params=(self.hashed_token,)
        )

        print(record)

        self.user_id = record["user_id"]
        self.user_email = record["email"]




    async def get_most_recent_backup(self):
        record = await self.db.fetch_one(
            query="""
                  SELECT *
                  FROM backups
                  WHERE user_id = %s
                  ORDER BY created_at DESC LIMIT 1
                  """,
            params=(self.user_id,)
        )

        if record is not None:
            self.most_recent_backup = record["created_at"]

    async def handle(self, request: Request) -> JSONResponse:
        payload = await request.json()

        self.raw_token = payload["token"]
        self.hashed_token = hashlib.sha256(self.raw_token.encode()).hexdigest()

        await self.fetch_user_information()

        await self.get_most_recent_backup()

        return JSONResponse(
            status_code=200,
            content={
                "user_id": self.user_id,
                "email": self.user_email,
                "most_recent_backup": str(self.most_recent_backup),
            }
        )
