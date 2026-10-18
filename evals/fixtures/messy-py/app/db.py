import sqlite3


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        create table if not exists customers (id integer primary key, email text, vip integer default 0);
        create table if not exists orders (id integer primary key, customer_id integer, subtotal_cents integer, created text);
        """
    )
    return conn
