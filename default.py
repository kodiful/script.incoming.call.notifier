# -*- coding: utf-8 -*-

import sys
import urlparse
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

from resources.lib.common import *
from resources.lib.history import History
from resources.lib.phonebook import PhoneBook
from resources.lib.const import Const


if __name__  == '__main__':

    # 引数
    args = urlparse.parse_qs(sys.argv[2][1:], keep_blank_values=True)
    for key in args.keys():
        args[key] = args[key][0]
    action = args.get('action', 'showHistory')

    # アドオン設定
    settings = {}
    for key in ('key','name'):
        settings[key] = Const.GET(key)
    Const.SET('key','')
    Const.SET('name','')
    Const.SET('mode','create')

    # actionに応じた処理

    # 着信履歴
    if action == 'showHistory':
        History().show()
    elif action == 'clearHistory':
        History().clear()
        xbmc.executebuiltin('Container.Refresh()')

    # 電話帳
    elif action == 'showPhoneBook':
        PhoneBook().show()
    elif action == 'addPhoneBookItem':
        PhoneBook().beginEdit(
            key=args.get('key'),
            name=args.get('name'),
            mode='add')
    elif action == 'beginEditPhoneBookItem':
        PhoneBook().beginEdit(
            key=args.get('key'),
            name=args.get('name'),
            mode='edit')
    elif action == 'endEditPhoneBookItem':
        PhoneBook().endEdit(
            key=settings.get('key'),
            name=settings.get('name'))
        History().update(
            key=settings.get('key'),
            name=settings.get('name'))
        xbmc.executebuiltin('Container.Refresh()')
    elif action == 'removePhoneBookItem':
        PhoneBook().remove(
            key=args.get('key'))
        History().update(
            key=args.get('key'),
            name=args.get('key'))
        xbmc.executebuiltin('Container.Refresh()')

    # キャッシュ
    elif action == 'clearCache':
        PhoneBook(Const.CACHE_FILE).clear()
        xbmc.executebuiltin('Container.Refresh()')

    # 設定画面
    elif action == 'clearCustomSearch':
        Const.SET('customsearch','')
    elif action == 'settings':
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % Const.ADDON_ID)
