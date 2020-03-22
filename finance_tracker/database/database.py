"""Functions to interface with an SQLite database

"""

import sqlite3

def create_database(file_path):
    conn = sqlite3.connect(file_path)

    with open("schema.sql", r) as schema_file:
        schema = schema_file.read()

    conn.execute(schema)


def read_balance():
    pass


def write_balance():
    pass


def read_transaction():
    pass


def write_transaction():
    pass


def list_categories():
    pass


def list_subcategories():
    pass



