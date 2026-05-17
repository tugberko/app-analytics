import json
from typing import Optional

from utils.database_connection import MySQLClient


class BackupRestoreService:

    def __init__(self):
        self.db = MySQLClient()


    async def backup(self, user_id: int, data: dict):

        await self.db.insert_and_get_id(
            query="INSERT INTO backups (user_id, data) VALUES (%s, %s)",
            params=(user_id, json.dumps(data))
        )

    async def restore(self, user_id: int) -> Optional[dict]:

        record = await self.db.fetch_one(
            query="SELECT * FROM backups WHERE user_id = %s ORDER BY id DESC LIMIT 1",
            params=(user_id,)
        )

        if record is None:
            # No backups found
            return {
                "last_backup_date" : None,
                "data": None
            }

        return {
            "last_backup_date": str(record["created_at"]),
            "data": json.loads(record["data"])
        }

    async def get_most_recent_backup_date(self, user_id: int) -> Optional[str]:

        record = await self.db.fetch_one(
            query="SELECT MAX(created_at) AS most_recent_backup_date FROM backups WHERE user_id = %s",
            params=(user_id,)
        )

        print(record)

        if record is not None:
            return str(record["most_recent_backup_date"])

        return None

