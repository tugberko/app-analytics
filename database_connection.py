import os
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import aiomysql


class MySQLClient:
    """
    Async MySQL client using:
    - aiomysql
    - environment variables
    - connection pooling

    Required environment variables:
        DB_HOST
        DB_PORT
        DB_USER
        DB_PASSWORD
        DB_NAME

    Optional:
        DB_MIN_POOL_SIZE
        DB_MAX_POOL_SIZE
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

    async def connect(self) -> None:
        """Initialize connection pool."""
        if self.pool is not None:
            return

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
        """
        Execute INSERT/UPDATE/DELETE query.

        Returns:
            Number of affected rows.
        """
        if not self.pool:
            raise RuntimeError("Connection pool is not initialized.")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params)
                return cur.rowcount

    async def fetch_one(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row.
        """
        if not self.pool:
            raise RuntimeError("Connection pool is not initialized.")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchone()

    async def fetch_all(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch all rows.
        """
        if not self.pool:
            raise RuntimeError("Connection pool is not initialized.")

        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, params)
                return await cur.fetchall()

    async def executemany(
        self,
        query: str,
        params: Sequence[Union[Tuple, Dict]],
    ) -> int:
        """
        Execute bulk insert/update operations.

        Returns:
            Number of affected rows.
        """
        if not self.pool:
            raise RuntimeError("Connection pool is not initialized.")

        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, params)
                return cur.rowcount

    async def transaction(self):
        """
        Acquire transactional connection manually.

        Usage:
            async with db.transaction() as conn:
                ...
        """
        if not self.pool:
            raise RuntimeError("Connection pool is not initialized.")

        return self.pool.acquire()