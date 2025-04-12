# -*- coding: utf-8 -*-

import sys
import re
import xbmcgui
import xbmcplugin

from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.db import DB
from resources.lib.phonebook import PhoneBook


class History(Common):

    def __init__(self):
        return

    def append(self, uri, key, name):
        db = DB()
        db.add_to_history(db.now(), key, name, uri)
        db.conn.close()

    def update(self, key, name):
        db = DB()
        sql = 'UPDATE history SET name = :name WHERE key = :key'
        db.cursor.execute(sql, {'key': key, 'name': name})
        db.conn.close()

    def clear(self):
        db = DB()
        db.cursor.execute('DELETE FROM history')
        db.conn.close()

    def show(self):
        db = DB()
        sql = 'SELECT date, key, name FROM history ORDER BY date DESC'
        db.cursor.execute(sql)
        for date, key, name in db.cursor.fetchall():
            # コンテクストメニュー
            menu = []
            if re.compile('^0[0-9]{8,}').search(key):
                if PhoneBook().lookup(key):
                    action = 'RunPlugin({url}?action=beginEditPhoneBookItem&{query})'.format(url=sys.argv[0], query=urlencode({
                        'key': key,
                        'name': name
                    }))
                    menu.append((Common.STR(32904), action))
                    name = f'[COLOR lightgreen]{name} <{key}>[/COLOR]'
                else:
                    action = 'RunPlugin({url}?action=addPhoneBookItem&{query})'.format(url=sys.argv[0], query=urlencode({
                        'key': key,
                        'name': name
                    }))
                    menu.append((Common.STR(32903), action))
                    name = f'[COLOR khaki]{name} <{key}>[/COLOR]'
            else:
                name = f'[COLOR orange]{name}[/COLOR]'
            action = 'Container.Update(%s?action=showPhoneBook)' % (sys.argv[0])
            menu.append((Common.STR(32907), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Common.STR(32902), action))
            # リストアイテム
            date = db.convert(date, Common.STR(32900))
            li = xbmcgui.ListItem(f'{date}  {name}')
            li.setArt({'icon': self.RINGER_VOLUME, 'thumb': self.RINGER_VOLUME})
            li.addContextMenuItems(menu, replaceItems=True)
            # 履歴 - 追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        db.conn.close()
