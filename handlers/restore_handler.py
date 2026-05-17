import hashlib
import json
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from utils.database_connection import MySQLClient


class RestoreHandler:
    FAILURE_RESPONSE = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False}
    )

    def __init__(self):

        self.hashed_token = None
        self.raw_token = None

        self.user_id: Optional[int] = None

        self.most_recent_data: Optional[dict] = None
        self.most_recent_restore_date: str = None

        self.db = MySQLClient()

    async def find_user(self):

        record = await self.db.fetch_one(
            query="SELECT * FROM tokens WHERE token_hash=%s AND CURDATE() < expires_at",
            params=(self.hashed_token,)
        )

        if record is None:
            print("No users found with this token")
            return

        self.user_id = record["user_id"]

    async def restore(self):

        record = await self.db.fetch_one(
            query = "SELECT * FROM backups B WHERE B.user_id = %s ORDER BY B.created_at DESC LIMIT 1",
            params=(self.user_id,)
        )

        if record is not None:
            self.most_recent_data = json.loads(record["data"])
            self.most_recent_restore_date = str(record["created_at"])


    async def handle(self, request: Request) -> JSONResponse:

        payload = await request.json()
        
        self.raw_token = payload["token"]
        self.hashed_token = hashlib.sha256(self.raw_token.encode()).hexdigest()


        await self.find_user()

        if self.user_id is not None:
            await self.restore()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "most_recent_restore_date": self.most_recent_restore_date,
                    "most_recent_data": self.most_recent_data,
                    "success": True
                }
            )

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"success": False})

