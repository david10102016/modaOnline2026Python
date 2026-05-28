import psycopg2
import psycopg2.extras
import bcrypt
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

class Cursor:
    def __init__(self, cur):
        self._cur = cur

    def fetchone(self):
        try:
            row = self._cur.fetchone()
        except Exception:
            return None
        if row is None:
            return None
        return _IndexableDict(row)

    def fetchall(self):
        rows = self._cur.fetchall()
        return [_IndexableDict(r) for r in rows]

    def execute(self, query, params=()):
        query = query.replace('?', '%s')
        self._cur.execute(query, params)
        return self

    @property
    def lastrowid(self):
        self._cur.execute("SELECT lastval()")
        return self._cur.fetchone()[0]

class _IndexableDict(dict):
    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)

class Connection:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, params=()):
        query = query.replace('?', '%s')
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params)
        return Cursor(cur)

    def executemany(self, query, params_list):
        query = query.replace('?', '%s')
        cur = self._conn.cursor()
        cur.executemany(query, params_list)

    def cursor(self):
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return Cursor(cur)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return Connection(conn)

def init_database():
    pass

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))