# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

from resources.lib.common import Common


class DB(Common):

    sql_cache = '''
    CREATE TABLE IF NOT EXISTS cache(
        key TEXT PRIMARY KEY,
        name TEXT,
        modified TEXT
    )'''

    sql_phonebook = '''
    CREATE TABLE IF NOT EXISTS phonebook(
        key TEXT PRIMARY KEY,
        name TEXT,
        modified TEXT
    )'''

    sql_history = '''
    CREATE TABLE IF NOT EXISTS history(
        date TEXT PRIMARY KEY,
        key TEXT,
        name TEXT,
        uri TEXT
    )'''

    sql_holidays = '''
    CREATE TABLE IF NOT EXISTS holidays(
        date TEXT,
        name TEXT
    )'''

    def __init__(self):
        # DBへ接続
        self.conn = sqlite3.connect(self.DB_PATH, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # テーブルを初期化
        self.cursor.execute(self.sql_cache)
        self.cursor.execute(self.sql_phonebook)
        self.cursor.execute(self.sql_history)
        self.cursor.execute(self.sql_holidays)

    def add_to_cache(self, key, name):
        values = {
            'key': key,
            'name': name,
            'modified': self.now()
        }
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR IGNORE INTO cache ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))
    
    def add_to_phonebook(self, key, name):
        values = {
            'key': key,
            'name': name,
            'modified': self.now()
        }
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR IGNORE INTO phonebook ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))

    def add_to_history(self, date, key, name, uri):
        values = {
            'date': date or self.now(),
            'key': key,
            'name': name,
            'uri': uri
        }
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR IGNORE INTO history ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))

    def now(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")  # 2025-02-22 05:35:43
    
    def add_holiday(self, values):
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT INTO holidays ({columns}) VALUES ({placeholders})'
        self.cursor.execute(sql, list(values.values()))