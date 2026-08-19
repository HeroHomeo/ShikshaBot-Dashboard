import asyncpg
import os
import re
import asyncio

_pool = None

async def init_pool():
    global _pool
    db_url = os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/shikshabot")
    _pool = await asyncpg.create_pool(dsn=db_url)

class AsyncpgCursor:
    def __init__(self, conn):
        self.conn = conn
        self._fetchall = []
        self._fetchone = None
        self.rowcount = 0

    def _convert_query(self, query):
        # Convert SQLite `?` to PostgreSQL `$1`, `$2`
        parts = query.split('?')
        if len(parts) == 1:
            return query
        new_query = parts[0]
        for i in range(1, len(parts)):
            new_query += f'${i}' + parts[i]
        
        # Also convert AUTOINCREMENT to SERIAL
        new_query = new_query.replace("AUTOINCREMENT", "SERIAL")
        new_query = new_query.replace("INTEGER PRIMARY KEY SERIAL", "SERIAL PRIMARY KEY")
        new_query = new_query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        
        return new_query

    async def execute(self, query, params=()):
        if not isinstance(params, (tuple, list)):
            params = (params,)
            
        query = self._convert_query(query)
        
        try:
            if query.strip().upper().startswith("SELECT") or "RETURNING" in query.upper():
                res = await self.conn.fetch(query, *params)
                self._fetchall = [tuple(r.values()) for r in res]
                self._fetchone = tuple(res[0].values()) if res else None
            else:
                status = await self.conn.execute(query, *params)
                if status.startswith("INSERT") or status.startswith("UPDATE") or status.startswith("DELETE"):
                    try:
                        self.rowcount = int(status.split()[-1])
                    except:
                        pass
        except Exception as e:
            print(f"[DB Error] Query: {query} | Params: {params} | Error: {e}")
            raise e

    async def fetchone(self):
        return self._fetchone

    async def fetchall(self):
        return self._fetchall

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class AsyncpgConnection:
    def __init__(self):
        self.conn = None

    async def __aenter__(self):
        global _pool
        if _pool is None:
            await init_pool()
        self.conn = await _pool.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await _pool.release(self.conn)

    def cursor(self):
        return AsyncpgCursor(self.conn)
        
    async def execute(self, query, params=()):
        cur = AsyncpgCursor(self.conn)
        await cur.execute(query, params)
        return cur
            
    async def commit(self):
        pass

    async def close(self):
        pass

def connect(*args, **kwargs):
    # Ignore path args like 'db/automod.db'
    return AsyncpgConnection()
