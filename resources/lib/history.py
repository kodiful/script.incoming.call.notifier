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
            date1 = h['date']
            time1 = h['time']
            weekday = h['weekday']
            uri1 = h['uri']
            key1 = h['key']
            name1 = h['name']
            datetime = '%s(%s) %s' % (date1, w[weekday], time1)
            # コンテクストメニュー
            menu = []
            if re.compile('^0[0-9]{8,}').search(key1):
                if PhoneBook().lookup(key1):
                    template2 = '[COLOR limegreen]%s[/COLOR]'
                    action = 'RunPlugin(%s?action=beginEditPhoneBookItem&key=%s&name=%s)' % (sys.argv[0], urllib.quote_plus(key1), urllib.quote_plus(name1))
                    menu.append((Const.STR(32904), action))
                else:
                    template2 = '[COLOR yellow]%s[/COLOR]'
                    action = 'RunPlugin(%s?action=addPhoneBookItem&key=%s&name=%s)' % (sys.argv[0], urllib.quote_plus(key1), urllib.quote_plus(name1))
                    menu.append((Const.STR(32903), action))
            else:
                key1 = ''
                template2 = '[COLOR orange]%s[/COLOR]'
            action = 'Container.Update(%s?action=showPhoneBook)' % (sys.argv[0])
            menu.append((Const.STR(32907), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Const.STR(32902), action))
            # 書式
            if isholiday(date1) or weekday == 6:
                template1 = '[COLOR red]%s[/COLOR]'
            elif weekday == 5:
                template1 = '[COLOR blue]%s[/COLOR]'
            else:
                template1 = '%s'
            template3 = '%s'
            template = '%s  %s  %s' % (template1, template2, template3)
            title = template % (datetime, name1, key1)
            li = xbmcgui.ListItem(title, iconImage=Const.RINGER_VOLUME, thumbnailImage=Const.RINGER_VOLUME)
            li.addContextMenuItems(menu, replaceItems=True)
            # 履歴 - 追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
