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
        sql = '''SELECT his.date, his.key, his.name, hol.name
        FROM history as his LEFT JOIN holidays AS hol ON SUBSTR(his.date, 1, 10) = hol.date
        ORDER BY his.date DESC'''
        db.cursor.execute(sql)
        for date, key, name, holiday in db.cursor.fetchall():
            # 曜日
            w = self.weekday(date)
            # コンテクストメニュー
            menu = []
            if re.compile('^0[0-9]{8,}').search(key):
                if PhoneBook().lookup(key):
                    template2 = '[COLOR lightgreen]%s[/COLOR]'
                    action = 'RunPlugin({url}?action=beginEditPhoneBookItem&{query})'.format(url=sys.argv[0], query=urlencode({
                        'key': key,
                        'name': name
                    }))
                    menu.append((Common.STR(32904), action))
                else:
                    template2 = '[COLOR khaki]%s[/COLOR]'
                    action = 'RunPlugin({url}?action=addPhoneBookItem&{query})'.format(url=sys.argv[0], query=urlencode({
                        'key': key,
                        'name': name
                    }))
                    menu.append((Common.STR(32903), action))
            else:
                key = ''
                template2 = '[COLOR orange]%s[/COLOR]'
            action = 'Container.Update(%s?action=showPhoneBook)' % (sys.argv[0])
            menu.append((Common.STR(32907), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Common.STR(32902), action))
            # 書式
            if holiday or w == 6:
                template1 = '[COLOR red]%s[/COLOR]'
            elif w == 5:
                template1 = '[COLOR blue]%s[/COLOR]'
            else:
                template1 = '%s'
            template3 = '%s'
            template = '%s  %s  %s' % (template1, template3, template2)
            title = re.sub(r'\s{2,}', '  ', template % (date, key, name))
            li = xbmcgui.ListItem(title)
            li.setArt({'icon': self.RINGER_VOLUME, 'thumb': self.RINGER_VOLUME})
            li.addContextMenuItems(menu, replaceItems=True)
            # 履歴 - 追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        db.conn.close()
