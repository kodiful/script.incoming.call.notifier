# -*- coding: utf-8 -*-

import sys
import os
import re
import urllib
import datetime
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from common import *
from const import Const
from phonebook import PhoneBook


class History:

    def __init__(self, filepath=Const.HISTORY_FILE):
        self.filepath = filepath
        self.read()

    def read(self):
        self.data = read_json(self.filepath) or []

    def write(self):
        write_json(self.filepath, self.data)

    def append(self, uri, key, name):
        now = datetime.datetime.now()
        self.data.append({
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'weekday': now.weekday(),
            'uri': uri,
            'key': key,
            'name': name,
        })
        self.write()

    def update(self, key, name):
        for data in self.data:
            if data['key'] == key: data['name'] = name
        self.write()

    def clear(self):
        self.data = []
        self.write()

    def show(self):
        # 曜日表記
        w = Const.STR(32900).split(',')
        # 履歴表示
        for h in reversed(self.data):
            # 履歴
            date = h['date']
            time = h['time']
            wday = h['weekday']
            uri = h['uri']
            key = h['key']
            name = h['name']
            datetime = '%s(%s) %s' % (date, w[wday], time)
            # コンテクストメニュー
            menu = []
            if re.compile('^0[0-9]{8,}').search(key):
                if PhoneBook().lookup(key):
                    template2 = '[COLOR lightgreen]%s[/COLOR]'
                    action = 'RunPlugin({url}?action=beginEditPhoneBookItem&{query})'.format(url=sys.argv[0], query=urllib.urlencode({
                        'key': key,
                        'name': name
                    }))
                    menu.append((Const.STR(32904), action))
                else:
                    template2 = '[COLOR khaki]%s[/COLOR]'
                    action = 'RunPlugin({url}?action=addPhoneBookItem&{query})'.format(url=sys.argv[0], query=urllib.urlencode({
                        'key': key,
                        'name': name
                    }))
                    menu.append((Const.STR(32903), action))
            else:
                key = ''
                template2 = '[COLOR orange]%s[/COLOR]'
            action = 'Container.Update(%s?action=showPhoneBook)' % (sys.argv[0])
            menu.append((Const.STR(32907), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Const.STR(32902), action))
            # 書式
            if isholiday(date) or wday == 6:
                template1 = '[COLOR red]%s[/COLOR]'
            elif wday == 5:
                template1 = '[COLOR blue]%s[/COLOR]'
            else:
                template1 = '%s'
            template3 = '%s'
            template = '%s  %s  %s' % (template1, template3, template2)
            title = template % (datetime, key, name)
            li = xbmcgui.ListItem(title, iconImage=Const.RINGER_VOLUME, thumbnailImage=Const.RINGER_VOLUME)
            li.addContextMenuItems(menu, replaceItems=True)
            # 履歴 - 追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
