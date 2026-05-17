from starlette.responses import JSONResponse
from fastapi import Request

from services.backup_restore_service import BackupRestoreService
from services.token_service import TokenService
from services.user_service import UserService
from utils.database_connection import MySQLClient


class MeHandler:

    def __init__(self):
        self.db = MySQLClient()

    async def handle(self, request: Request) -> JSONResponse:
        payload = await request.json()

        token_service = TokenService()
        user_id = await token_service.find_user(payload["token"])

        if user_id is None:
            return JSONResponse(status_code=400,
                                content={"user_id": None, "email": None, "most_recent_backup_date": None})

        user_service = UserService()
        email = await user_service.find_email_by_user_id(user_id)

        backup_restore_service = BackupRestoreService()
        most_recent_backup_date = await backup_restore_service.get_most_recent_backup_date(user_id)

        return JSONResponse(
            status_code=200,
            content={
                "user_id": user_id,
                "email": email,
                "most_recent_backup_date": most_recent_backup_date,
            }
        )
