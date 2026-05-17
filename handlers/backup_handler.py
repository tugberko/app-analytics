import hashlib
import json
from typing import Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette import status

from services.backup_restore_service import BackupRestoreService
from services.token_service import TokenService
from utils.database_connection import MySQLClient
from utils.hash import digest


class BackupHandler:
    FAILURE_RESPONSE = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"success": False}
    )

    def __init__(self):

        self.db = MySQLClient()



    async def handle(self, request: Request) -> JSONResponse:

        payload = await request.json()

        raw_token = payload["token"]

        token_service = TokenService()
        backup_restore_service = BackupRestoreService()

        user_id = await token_service.find_user(raw_token=raw_token)

        if user_id is None:
            return BackupHandler.FAILURE_RESPONSE

        await backup_restore_service.backup(user_id=user_id, data=payload["data"])

        return JSONResponse(status_code=status.HTTP_200_OK, content={"success": True})

