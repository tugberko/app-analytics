import asyncio
from fastapi import Request
from pymysql.err import IntegrityError  # adjust if needed

from database_connection import MySQLClient


class HeartbeatHandler:

    def __init__(self):
        self.db = MySQLClient()

    # -------------------------
    # GENERIC SAFE GET-OR-CREATE
    # -------------------------

    async def _get_or_create_id(
        self,
        select_query: str,
        select_params: tuple,
        insert_query: str,
        insert_params: tuple,
    ) -> int:

        row = await self.db.fetch_one(select_query, select_params)
        if row:
            return row["id"]

        try:
            return await self.db.insert_and_get_id(
                query=insert_query,
                params=insert_params,
            )

        except IntegrityError:
            row = await self.db.fetch_one(select_query, select_params)
            return row["id"]

    # -------------------------
    # LOOKUPS
    # -------------------------

    async def _get_or_create_platform_id(self, platform: str) -> int:
        return await self._get_or_create_id(
            select_query="""
                SELECT id FROM platforms WHERE name = %s
            """,
            select_params=(platform,),
            insert_query="""
                INSERT INTO platforms (name)
                VALUES (%s)
            """,
            insert_params=(platform,),
        )

    async def _get_or_create_version_id(self, version: str) -> int:
        return await self._get_or_create_id(
            select_query="""
                SELECT id FROM versions WHERE version = %s
            """,
            select_params=(version,),
            insert_query="""
                INSERT INTO versions (version)
                VALUES (%s)
            """,
            insert_params=(version,),
        )

    async def _get_or_create_locale_id(self, locale: str) -> int:
        return await self._get_or_create_id(
            select_query="""
                SELECT id FROM locales WHERE locale = %s
            """,
            select_params=(locale,),
            insert_query="""
                INSERT INTO locales (locale)
                VALUES (%s)
            """,
            insert_params=(locale,),
        )

    # -------------------------
    # APP INSTALLATION
    # -------------------------

    async def _get_or_create_app_installation_id(self, payload: dict) -> int:

        platform_id, locale_id = await asyncio.gather(
            self._get_or_create_platform_id(platform=payload["platform"]),
            self._get_or_create_locale_id(locale=payload["locale"]),
        )

        return await self._get_or_create_id(
            select_query="""
                SELECT id
                FROM app_installations
                WHERE install_uuid = %s
            """,
            select_params=(payload["install_uuid"],),
            insert_query="""
                INSERT INTO app_installations (
                    install_uuid,
                    platform_id,
                    locale_id
                )
                VALUES (%s, %s, %s)
            """,
            insert_params=(
                payload["install_uuid"],
                platform_id,
                locale_id,
            ),
        )

    # -------------------------
    # HEARTBEAT INSERT
    # -------------------------

    async def _create_heartbeat(self, payload: dict) -> int:

        app_installation_id, version_id = await asyncio.gather(
            self._get_or_create_app_installation_id(payload=payload),
            self._get_or_create_version_id(version=payload["version"]),
        )

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
                payload["local_time"],
                payload["time_since_last_startup"],
            ),
        )

    # -------------------------
    # PUBLIC HANDLER
    # -------------------------

    async def handle_heartbeat(self, request: Request):
        payload = await request.json()

        heartbeat_id = await self._create_heartbeat(payload=payload)

        return {
            "ok": True,
            "heartbeat_id": heartbeat_id,
        }