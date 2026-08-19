import psycopg2
from psycopg2 import pool
import psycopg2.extras
import os
import threading

_pool = None
_pool_lock = threading.Lock()

def _get_pool():
    global _pool
    with _pool_lock:
        if _pool is None:
            db_url = os.getenv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/shikshabot")
            try:
                if "?" not in db_url: db_url += "?sslmode=require"
                _pool = psycopg2.pool.ThreadedConnectionPool(1, 3, dsn=db_url)
            except Exception as e:
                print(f"[FATAL] Could not connect to PostgreSQL sync: {e}")
    return _pool

def _convert_query(query):
    # Convert SQLite `?` to PostgreSQL `%s`
    query = query.replace('?', '%s')
    query = query.replace("AUTOINCREMENT", "SERIAL")
    query = query.replace("INTEGER PRIMARY KEY SERIAL", "SERIAL PRIMARY KEY")
    query = query.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    query = query.replace("INSERT OR IGNORE", "INSERT") # Postgres handles this with ON CONFLICT, but we'll try to let it fail silently if ignored
    return query

class MockCursorSync:
    def __init__(self, cur):
        self.cur = cur

    def execute(self, query, params=()):
        if not isinstance(params, (tuple, list)):
            params = (params,)
        query = _convert_query(query)
        try:
            self.cur.execute(query, params)
        except psycopg2.IntegrityError:
            self.cur.connection.rollback() # If it was an INSERT OR IGNORE duplicate
        except Exception as e:
            self.cur.connection.rollback()
            
    def fetchone(self):
        try:
            return self.cur.fetchone()
        except:
            return None

    def fetchall(self):
        try:
            return self.cur.fetchall()
        except:
            return []
            
    @property
    def rowcount(self):
        return self.cur.rowcount

    def close(self):
        self.cur.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

class MockConnectionSync:
    def __init__(self):
        self.pool = _get_pool()
        self.conn = None
        if self.pool:
            self.conn = self.pool.getconn()
            self.conn.autocommit = True
        self.row_factory = None # Placeholder for sqlite3.Row compatibility

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None and self.conn:
            try:
                self.conn.rollback()
            except:
                pass

    def cursor(self):
        if not self.conn:
            return None
        return MockCursorSync(self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor))
        
    def execute(self, query, params=()):
        if not self.conn:
            return None
        cur = MockCursorSync(self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor))
        cur.execute(query, params)
        return cur
            
    def commit(self):
        if self.conn:
            self.conn.commit()

    def close(self):
        if self.conn and self.pool:
            self.pool.putconn(self.conn)
            self.conn = None
            
def connect(*args, **kwargs):
    return MockConnectionSync()

class Error(Exception):
    pass
class OperationalError(Error):
    pass
class Row:
    pass
