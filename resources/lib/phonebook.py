# -*- coding: utf-8 -*-

import sys
import os
import shutil
import xbmc
import xbmcgui
import xbmcplugin

from urllib.parse import quote_plus

from resources.lib.common import Common
from resources.lib.db import DB


class PhoneBook(Common):

    def __init__(self, cache=False):
        self.table = 'cache' if cache else 'phonebook'

    def lookup(self, key=None):
        db = DB()
        sql = f'SELECT name FROM {self.table} WHERE key = :key'
        db.cursor.execute(sql, {'key': key})
        name = db.cursor.fetchone()
        db.conn.close()
        return name and name[0]
    
    def update(self, key, name):
        db = DB()
        sql = f'UPDATE {self.table} SET name = :name WHERE key = :key'
        db.cursor.execute(sql, {'key': key, 'name': name})
        db.conn.close()
        return name

    def remove(self, key):
        db = DB()
        db.cursor.execute(f'DELETE FROM {self.table} WHERE key = :key', {'key': key})
        db.conn.close()

    def clear(self):
        db = DB()
        db.cursor.execute(f'DELETE FROM {self.table}')
        db.conn.close()

    def show(self):
        db = DB()
        sql = f'SELECT key, name FROM {self.table} ORDER BY key'
        db.cursor.execute(sql)
        for key, name in db.cursor.fetchall():
            # 電話帳エントリ - リストアイテム
            title = '%s [COLOR lightgreen]%s[/COLOR]' % (key, name)
            li = xbmcgui.ListItem(title)
            li.setArt({'icon': self.CONTACTS, 'thumb': self.CONTACTS})
            # 履歴 - コンテクストメニュー
            menu = []
            action = 'RunPlugin(%s?action=beginEditPhoneBookItem&key=%s&name=%s)' % (sys.argv[0], quote_plus(key), quote_plus(name))
            menu.append((self.STR(32905), action))
            action = 'RunPlugin(%s?action=removePhoneBookItem&key=%s&name=%s)' % (sys.argv[0], quote_plus(key), quote_plus(name))
            menu.append((self.STR(32906), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((self.STR(32902), action))
            li.addContextMenuItems(menu, replaceItems=True)
            # リストアイテムを追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        db.conn.close()

    def beginEdit(self, key, name, mode):
        self.SET('key', key)
        self.SET('name', name)
        self.SET('mode', mode)  # modeはコンテクストに応じた設定画面表示のために使用
        settings_path = os.path.join(self.RESOURCES_PATH, 'settings.xml')
        shutil.copy(os.path.join(self.DATA_PATH, 'settings', 'edit.xml'), settings_path)
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % self.ADDON_ID)
        xbmc.sleep(1000)
        shutil.copy(os.path.join(self.DATA_PATH, 'settings', 'default.xml'), settings_path)

    def endEdit(self, key, name):
        db = DB()
        values = {
            'key': key,
            'name': name,
            'modified': db.now()
        }
        columns = ', '.join(values.keys())
        placeholders = ', '.join(['?' for _ in values])
        sql = f'INSERT OR REPLACE INTO {self.table} ({columns}) VALUES ({placeholders})'
        db.cursor.execute(sql, list(values.values()))
        db.conn.close()