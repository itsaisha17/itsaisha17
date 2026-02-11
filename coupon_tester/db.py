from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from psycopg import Connection


@contextmanager
def get_connection(dsn: str) -> Generator[Connection, None, None]:
    conn = Connection.connect(dsn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
