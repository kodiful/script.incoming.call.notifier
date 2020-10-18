# -*- coding: utf-8 -*-

import urlparse, urllib
import sys, re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from resources.lib.common import log, isholiday
from resources.lib.history import History
from resources.lib.phonebook import PhoneBook
from resources.lib.lookup import Lookup
from resources.lib.const import Const

#-------------------------------------------------------------------------------
def main():
    # パラメータ抽出
    args = urlparse.parse_qs(sys.argv[2][1:])
    action = args.get('action', None)
    # アドオン設定
    key = Const.GET('key') #str
    name = Const.GET('name')
    mode = Const.GET('mode')
    Const.SET('key','')
    Const.SET('name','')
    Const.SET('mode','create')

    if action is None:
        # 曜日表記
        w = Const.STR(32900).encode('utf-8').split(',')
        # 履歴
        phonebook = PhoneBook('phonebook.json')
        history = History('history.json')
        length = len(history.data)
        # 履歴表示
        for i in range(0,length):
            # 履歴
            h = history.data[length-i-1]
            date1 = h['date'].encode('utf-8')
            time1 = h['time'].encode('utf-8')
            weekday = h['weekday']
            uri1 = h['uri'].encode('utf-8')
            key1 = h['key'].encode('utf-8')
            name1 = h['name'].encode('utf-8')
            datetime = '%s(%s) %s' % (date1, w[weekday], time1)
            # コンテクストメニュー
            menu = []
            if re.compile('^0[0-9]{8,}').search(key1):
                if phonebook.lookup(key1):
                    template2 = '[COLOR limegreen]%s[/COLOR]'
                    action = 'RunPlugin(%s?action=edit&key=%s&name=%s&mode=update)' % (sys.argv[0], urllib.quote_plus(key1), urllib.quote_plus(name1))
                    menu.append((Const.STR(32904), action))
                else:
                    template2 = '[COLOR yellow]%s[/COLOR]'
                    action = 'RunPlugin(%s?action=edit&key=%s&name=%s&mode=append)' % (sys.argv[0], urllib.quote_plus(key1), urllib.quote_plus(name1))
                    menu.append((Const.STR(32903), action))
            else:
                key1 = ''
                template2 = '[COLOR orange]%s[/COLOR]'
            action = 'Container.Update(%s?action=browse)' % (sys.argv[0])
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

    elif action[0] == 'browse':
        phonebook = PhoneBook('phonebook.json')
        items = sorted(phonebook.data.items())
        for key, name in items:
            key1 = key.encode('utf-8')
            name1 = name.encode('utf-8')
            # 電話帳エントリ - リストアイテム
            title = '[COLOR white]%s[/COLOR]  [COLOR limegreen]%s[/COLOR]' % (key1, name1)
            li = xbmcgui.ListItem(title, iconImage=Const.CONTACTS, thumbnailImage=Const.CONTACTS)
            # 履歴 - コンテクストメニュー
            menu = []
            action = 'RunPlugin(%s?action=edit&key=%s&name=%s&mode=update)' % (sys.argv[0], urllib.quote_plus(key1), urllib.quote_plus(name1))
            menu.append((Const.STR(32905), action))
            action = 'RunPlugin(%s?action=remove&key=%s&name=%s)' % (sys.argv[0], urllib.quote_plus(key1), urllib.quote_plus(name1))
            menu.append((Const.STR(32906), action))
            action = 'RunPlugin(%s?action=settings)' % (sys.argv[0])
            menu.append((Const.STR(32902), action))
            li.addContextMenuItems(menu, replaceItems=True)
            # リストアイテムを追加
            url = ''
            xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, listitem=li)
        # リストアイテム追加完了
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    elif action[0] == 'edit':
        key = args.get('key', None) #str
        name = args.get('name', None)
        mode = args.get('mode', None)
        Const.SET('key',key[0])
        Const.SET('name',name[0])
        Const.SET('mode',mode[0])
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)
        xbmc.executebuiltin('SetFocus(101)') # phonebook category which is the 2nd
        xbmc.executebuiltin('SetFocus(200)') # key control which is the 1st including hidden controls

    elif action[0] == 'update':
        if key and name:
            PhoneBook('phonebook.json').update(key, name)
        xbmc.executebuiltin('Container.Refresh()')

    elif action[0] == 'remove':
        key = args.get('key', None)
        name = args.get('name', None)
        if key and name:
            PhoneBook('phonebook.json').remove(key[0], name[0])
        xbmc.executebuiltin('Container.Refresh()')

    elif action[0] == 'clearCache':
        PhoneBook('cache.json').clear()
        xbmc.executebuiltin('Container.Refresh()')

    elif action[0] == 'clearHistory':
        History('history.json').clear()
        xbmc.executebuiltin('Container.Refresh()')

    elif action[0] == 'clearSearch':
        Const.SET('search','')

    elif action[0] == 'settings':
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)

#-------------------------------------------------------------------------------
if __name__  == '__main__': main()
