# -*- coding: utf-8 -*-

import sys
import os
import urllib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from common import *
from const import Const


class PhoneBook:

    def __init__(self, filepath=Const.PHONEBOOK_FILE):
        self.filepath = filepath
        self.read()

    def read(self):
        self.data = read_json(self.filepath) or {}

    def write(self):
        write_json(self.filepath, self.data)

    def lookup(self, key=None):
        return self.data.get(key) if key else None

    def remove(self, key):
        self.data.pop(key)
        self.write()

    def clear(self):
        self.data = {}
        self.write()

    def show(self):
        for key, name in sorted(self.data.items()):
            # 電話帳エントリ - リストアイテム
            title = '%s [COLOR lightgreen]%s[/COLOR]' % (key, name)
            li = xbmcgui.ListItem(title, iconImage=Const.CONTACTS, thumbnailImage=Const.CONTACTS)
            # 履歴 - コンテクストメニュー
            menu = []
            action = 'RunPlugin(%s?action=beginEditPhoneBookItem&key=%s&name=%s)' % (sys.argv[0], urllib.quote_plus(key), urllib.quote_plus(name))
            menu.append((Const.STR(32905), action))
            action = 'RunPlugin(%s?action=removePhoneBookItem&key=%s&name=%s)' % (sys.argv[0], urllib.quote_plus(key), urllib.quote_plus(name))
            menu.append((Const.STR(32906), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Const.STR(32902), action))
            li.addContextMenuItems(menu, replaceItems=True)
            # リストアイテムを追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def beginEdit(self, key, name, mode):
        Const.SET('key', key)
        Const.SET('name', name)
        Const.SET('mode', mode) # modeはコンテクストに応じた設定画面表示のために使用
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)
        xbmc.executebuiltin('SetFocus(101)') # phonebook category which is the 2nd
        xbmc.executebuiltin('SetFocus(200)') # key control which is the 1st including hidden controls

    def endEdit(self, key, name):
        self.data[key] = name
        self.write()
