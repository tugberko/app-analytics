from fastapi import Request
from database_connection import MySQLClient


class HeartbeatHandler:
    PLATFORM_MAP = {
        "iOS": 0,
        "Android": 1,
        "Other": 2,
    }

    def __init__(self):
        self.db = MySQLClient()

    async def _get_locale_id(self, locale: str) -> int:
        """

        :param locale:
        :return:
        """
        record = await self.db.fetch_one(
            query="""
                  SELECT id
                  FROM locales L
                  WHERE L.locale = %s
                  """,
            params=(locale,)
        )

        if record is not None:
            print("Already known locale")
            return record["id"]

        return await self._create_locale(locale)

    async def _create_locale(self, locale: str) -> int:
        print(f"Creating a new locale for {locale}")

        return await self.db.insert_and_get_id(
            query="""
                  INSERT INTO locales (locale)
                  VALUES (%s)
                  """,
            params=(
                locale,
            )
        )

    async def _create_app_installation(self, payload: dict) -> int:
        """
        This function creates a new record in app_installations table
        :param payload:
        :return:
        """

        print(f"Creating app_installation for UUID {payload['install_uuid']}")

        platform = payload.get("platform", "Other")
        platform_id = self.PLATFORM_MAP.get(platform, self.PLATFORM_MAP["Other"])

        locale_id = await self._get_locale_id(payload["locale"])

        return await self.db.insert_and_get_id(
            query="""
                  INSERT INTO app_installations (install_uuid, platform_id, locale_id)
                  VALUES (%s, %s, %s)
                  """,
            params=(
                payload["install_uuid"],
                platform_id,
                locale_id,
            ),
        )

    async def _get_app_installation_id(self, payload: dict) -> int:
        """
        This function gets the corresponding id from the app_installations table
        :param payload:
        :return:
        """
        record = await self.db.fetch_one(
            query="""
                  SELECT id
                  FROM app_installations
                  WHERE install_uuid = %s
                  """,
            params=(payload["install_uuid"],),
        )

        if record:
            print("Already known install UUID")
            return record["id"]

        return await self._create_app_installation(payload)

    async def _create_heartbeat(self, payload: dict) -> int:
        """
        This function creates a new record in heartbeats table
        :param payload:
        :return:
        """

        app_installation_id = await self._get_app_installation_id(payload)

        return await self.db.insert_and_get_id(
            query="""
                  INSERT INTO heartbeats (app_installation_id,
                                          created_at_local,
                                          time_since_last_startup_s)
                  VALUES (%s, %s, %s)
                  """,
            params=(
                app_installation_id,
                payload["local_time"],
                payload["time_since_last_startup"],
            ),
        )

    async def handle_heartbeat(self, request: Request):
        payload = await request.json()

        heartbeat_id = await self._create_heartbeat(payload)

        return {"ok": True, "heartbeat_id": heartbeat_id}
