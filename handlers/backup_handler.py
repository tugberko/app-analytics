import hashlib
import json
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from utils.database_connection import MySQLClient


class BackupHandler:
    FAILURE_RESPONSE = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False}
    )

    def __init__(self):
        self.user_data: dict = {}
        self.hashed_token = None
        self.raw_token = None

        self.user_id: Optional[int] = None

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

    async def backup(self):

        record = await self.db.insert_and_get_id(
            query="INSERT INTO backups (user_id, data) VALUES (%s, %s)",
            params=(self.user_id, json.dumps(self.user_data))
        )

        print(record)

    async def handle(self, request: Request) -> JSONResponse:

        payload = await request.json()
        
        self.raw_token = payload["token"]
        self.hashed_token = hashlib.sha256(self.raw_token.encode()).hexdigest()

        self.user_data = payload["user_data"]

        await self.find_user()

        if self.user_id is not None:
            await self.backup()
            return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"success": False})

