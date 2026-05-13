from fastapi import Request
from database_connection import MySQLClient


class HeartbeatHandler:
    PLATFORM_MAP = {
        "iOS": 1,
        "Android": 2,
        "Other": 3,
    }

    def __init__(self):
        self.db = MySQLClient()

    # -------------------------
    # UPSERT HELPERS (SAFE)
    # -------------------------

    async def _get_or_create_version_id(self, version: str) -> int:
        return await self.db.insert_and_get_id(
            query="""
                INSERT INTO versions (version)
                VALUES (%s)
                ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            params=(version,),
        )

    async def _get_or_create_locale_id(self, locale: str) -> int:
        return await self.db.insert_and_get_id(
            query="""
                INSERT INTO locales (locale)
                VALUES (%s)
                ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            params=(locale,),
        )

    async def _get_or_create_app_installation_id(self, payload: dict) -> int:
        platform = payload.get("platform", "Other")
        platform_id = self.PLATFORM_MAP.get(platform, self.PLATFORM_MAP["Other"])

        locale = payload["locale"]

        locale_id = await self._get_or_create_locale_id(locale)

        return await self.db.insert_and_get_id(
            query="""
                INSERT INTO app_installations (install_uuid, platform_id, locale_id)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)
            """,
            params=(
                payload["install_uuid"],
                platform_id,
                locale_id,
            ),
        )

    # -------------------------
    # HEARTBEAT INSERT
    # -------------------------

    async def _create_heartbeat(self, payload: dict) -> int:
        app_installation_id = await self._get_or_create_app_installation_id(payload)
        version_id = await self._get_or_create_version_id(payload["version"])

        # safer extraction (avoids KeyError surprises)
        local_time = payload["local_time"]
        time_since_last_startup = payload["time_since_last_startup"]

        return await self.db.insert_and_get_id(
            query="""
                INSERT INTO heartbeats (
                    app_installation_id,
                    version_id,
                    created_at_local,
                    time_since_last_startup_s
                )
                VALUES (%s, %s, %s, %s)
            """,
            params=(
                app_installation_id,
                version_id,
                local_time,
                time_since_last_startup,
            ),
        )

    # -------------------------
    # PUBLIC HANDLER
    # -------------------------

    async def handle_heartbeat(self, request: Request):
        payload = await request.json()

        heartbeat_id = await self._create_heartbeat(payload)

        return {
            "ok": True,
            "heartbeat_id": heartbeat_id,
        }