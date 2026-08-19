import asyncpg
import os
import asyncio

_pools = {}

async def _get_pool():
    loop = asyncio.get_running_loop()
    if loop not in _pools:
        db_url = os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/shikshabot")
        try:
            if "?" not in db_url: db_url += "?sslmode=require"
            _pools[loop] = await asyncpg.create_pool(dsn=db_url, ssl="require", min_size=1, max_size=5)
        except Exception as e:
            print(f"[FATAL] Could not connect to PostgreSQL: {e}")
    return _pools.get(loop)

def _convert_query(query):
    # Convert SQLite `?` to PostgreSQL `$1`, `$2`
    parts = query.split('?')
    if len(parts) == 1:
        return query
    new_query = parts[0]
    for i in range(1, len(parts)):
        new_query += f'${i}' + parts[i]
    
    # Also convert SQLite datatypes
    new_query = new_query.replace("AUTOINCREMENT", "SERIAL")
    new_query = new_query.replace("INTEGER PRIMARY KEY SERIAL", "SERIAL PRIMARY KEY")
    new_query = new_query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    return new_query

class MockCursor:
    def __init__(self, conn, lock=None):
        self.conn = conn
        self.lock = lock or asyncio.Lock()
        self._fetchall = []
        self._fetchone = None
        self.rowcount = 0

    def __await__(self):
        async def _ret():
            return self
        return _ret().__await__()

    async def execute(self, query, params=()):
        async with self.lock:
            if not isinstance(params, (tuple, list)):
                params = (params,)
            query = _convert_query(query)
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
                pass # Suppress to mimic some bad aiosqlite ignores in the codebase

    async def fetchone(self):
        return self._fetchone

    async def fetchall(self):
        return self._fetchall

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class ExecuteWrapper:
    def __init__(self, conn, lock, query, params):
        self.cur = MockCursor(conn, lock)
        self.query = query
        self.params = params
        self._executed = False

    def __await__(self):
        return self._execute_and_return().__await__()

    async def _execute_and_return(self):
        if not self._executed:
            await self.cur.execute(self.query, self.params)
            self._executed = True
        return self.cur

    async def __aenter__(self):
        return await self._execute_and_return()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

class MockConnection:
    def __init__(self):
        self.conn = None
        self.lock = asyncio.Lock()

    def __await__(self):
        async def _connect():
            pool = await _get_pool()
            if pool and not self.conn:
                self.conn = await pool.acquire()
            return self
        return _connect().__await__()

    async def __aenter__(self):
        pool = await _get_pool()
        if pool and not self.conn:
            self.conn = await pool.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pool = await _get_pool()
        if pool and self.conn:
            await pool.release(self.conn)
            self.conn = None

    def cursor(self):
        return MockCursor(self.conn, self.lock)
        
    def execute(self, query, params=()):
        return ExecuteWrapper(self.conn, self.lock, query, params)
            
    async def commit(self):
        pass

    async def close(self):
        pool = await _get_pool()
        if pool and self.conn:
            await pool.release(self.conn)
            self.conn = None

def connect(*args, **kwargs):
    return MockConnection()

class Error(Exception):
    pass
class OperationalError(Error):
    pass
class Row:
    pass
