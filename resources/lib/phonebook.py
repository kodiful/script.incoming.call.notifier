# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcgui
import xbmcplugin

from urllib.parse import quote_plus

from resources.lib.common import Common


class PhoneBook:

    def __init__(self, filepath=Common.PHONEBOOK_FILE):
        self.filepath = filepath
        self.read()

    def read(self):
        self.data = Common.read_json(self.filepath) or {}

    def write(self):
        Common.write_json(self.filepath, self.data)

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
            li = xbmcgui.ListItem(title)
            li.setArt({'icon': Common.CONTACTS, 'thumb': Common.CONTACTS})
            # 履歴 - コンテクストメニュー
            menu = []
            action = 'RunPlugin(%s?action=beginEditPhoneBookItem&key=%s&name=%s)' % (sys.argv[0], quote_plus(key), quote_plus(name))
            menu.append((Common.STR(32905), action))
            action = 'RunPlugin(%s?action=removePhoneBookItem&key=%s&name=%s)' % (sys.argv[0], quote_plus(key), quote_plus(name))
            menu.append((Common.STR(32906), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Common.STR(32902), action))
            li.addContextMenuItems(menu, replaceItems=True)
            # リストアイテムを追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def beginEdit(self, key, name, mode):
        Common.SET('key', key)
        Common.SET('name', name)
        Common.SET('mode', mode)  # modeはコンテクストに応じた設定画面表示のために使用
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Common.ADDON_ID)
        xbmc.executebuiltin('SetFocus(-99)')

    def endEdit(self, key, name):
        self.data[key] = name
        self.write()
