from fastapi import Request

from database_connection import MySQLClient


class HeartbeatHandler:

    def __init__(self):
        pass

    async def _handle_installation(self, install_uuid: str, platform_name: str) -> int:

        await MySQLClient().execute(
            """
                INSERT INTO app_installs (install_uuid, platform_id)
                SELECT %s, p.id
                FROM platforms p
                WHERE p.name = %s
                ON DUPLICATE KEY UPDATE
                    app_installs.id = LAST_INSERT_ID(app_installs.id);
            """,
            (install_uuid, platform_name)
        )

        row = await MySQLClient().fetch_one("SELECT LAST_INSERT_ID() AS install_id")
        return row["install_id"]

    async def handle(self, request: Request):
        payload = await request.json()

        await self._handle_installation(payload["install_uuid"], payload["platform"])

        return {"ok"}
