import psycopg2
import psycopg2.extras
import bcrypt
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

class ScalarCursor:
    """Cursor que permite [0] en fetchone() para queries COUNT/SUM"""
    def __init__(self, cur):
        self._cur = cur

    def fetchone(self):
        row = self._cur.fetchone()
        if row is None:
            return None
        return _IndexableDict(row)

    def fetchall(self):
        return self._cur.fetchall()

    @property
    def lastrowid(self):
        return self._cur.fetchone()

class _IndexableDict(dict):
    """Diccionario que también soporta acceso por índice numérico"""
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
        return ScalarCursor(cur)

    def executemany(self, query, params_list):
        query = query.replace('?', '%s')
        cur = self._conn.cursor()
        cur.executemany(query, params_list)
        return cur

    def cursor(self):
        cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return ScalarCursor(cur)

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