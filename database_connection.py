import os
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import aiomysql


class MySQLClient:
    """
    Async MySQL client using aiomysql with connection pooling.
    """

    def __init__(self):
        self.pool: Optional[aiomysql.Pool] = None

        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", 3306))
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASS", "")
        self.db = os.getenv("DB_NAME", "")

        self.minsize = int(os.getenv("DB_MIN_POOL_SIZE", 1))
        self.maxsize = int(os.getenv("DB_MAX_POOL_SIZE", 10))

    async def _ensure_pool(self) -> aiomysql.Pool:
        """
        Ensure the connection pool is initialized.
        """
        if self.pool is None:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                minsize=self.minsize,
                maxsize=self.maxsize,
                autocommit=True,
            )
        return self.pool

    async def close(self) -> None:
        """Close connection pool."""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            self.pool = None

    async def execute(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
    ) -> int:
        pool = await self._ensure_pool()

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.rowcount

    async def fetch_one(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
    ) -> Optional[Dict[str, Any]]:
        pool = await self._ensure_pool()

        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchone()

    async def fetch_all(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
    ) -> List[Dict[str, Any]]:
        pool = await self._ensure_pool()

        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

    async def executemany(
        self,
        query: str,
        params: Sequence[Union[Tuple, Dict]],
    ) -> int:
        pool = await self._ensure_pool()

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, params)
                return cur.rowcount

    async def insert_and_get_id(self, query: str, params=None) -> int:
        pool = await self._ensure_pool()

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.lastrowid

    async def transaction(self):
        """
        Transactional connection context manager.

        Usage:
            async with db.transaction() as conn:
                ...
        """
        pool = await self._ensure_pool()
        return pool.acquire()