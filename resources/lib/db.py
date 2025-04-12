# -*- coding: utf-8 -*-

import sqlite3
import locale
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

    # 祝祭日を判定する
    def is_holiday(self, date):
        sql = 'SELECT name FROM holidays WHERE date = :date'
        self.cursor.execute(sql, {'date': date})
        name = self.cursor.fetchone()
        return name

    def convert(self, timestamp, format, color=None):
        # timestamp: 2025-04-05 12:34:00
        # format: %Y年%m月%d日(%a) %H:%M
        # return: [COLOR blue]2025年04月05日(土) 12:34[/COLOR]
        locale.setlocale(locale.LC_ALL, '')  # 言語に応じた日付フォーマット用設定
        text = self.datetime(timestamp).strftime(format)
        w = self.weekday(timestamp)
        if color:
            text = f'[COLOR {color}]{text}[/COLOR]'
        elif self.is_holiday(timestamp[:10]):  # 祝祭日
            text = f'[COLOR red]{text}[/COLOR]'
        elif w == 6:  # 日曜日
            text = f'[COLOR red]{text}[/COLOR]'
        elif w == 5:  # 土曜日
            text = f'[COLOR blue]{text}[/COLOR]'
        return text