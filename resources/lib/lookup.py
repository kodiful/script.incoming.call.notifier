# -*- coding: utf-8 -*-

import sys, os, re
import urllib

import xbmc, xbmcaddon

from scrape import scrape
from phonebook import PhoneBook
from history import History

from common import log

# searchをインポート
addon = xbmcaddon.Addon()
path = addon.getSetting('search')
if os.path.isfile(path): sys.path.append(os.path.dirname(path))
from search import search

#-------------------------------------------------------------------------------
class Lookup:

    phonebook = None
    cache = None

    def __init__(self):
        self.history = History('history.json')

    def lookup(self, uri, cache=True, history=True):
        self.phonebook = PhoneBook('phonebook.json')
        self.cache = PhoneBook('cache.json')
        name = None
        key = None
        m = re.compile('"(.*)"\s*<(.*)>').search(uri)
        if m and m.group(1):
            key = m.group(1)
            # 0で始まって9桁以上ある場合は電話番号として先ず電話帳、次にキャッシュ、最後にウェブを検索
            if re.compile('^0[0-9]{8,}').search(key):
                # 電話帳を検索
                name = self.phonebook.lookup(key)
                if name is None:
                    # キャッシュを検索
                    name = self.cache.lookup(key)
                    if name is None:
                        # ウェブを検索
                        name = search(key) #unicode
                        if name is None:
                            pass
                        else:
                            if isinstance(name, unicode): name = name.encode('utf-8')
                            # キャッシュに追加
                            if cache: self.cache.update(key, name)
            elif key == 'Anonymous':
                #name = '非通知'
                name = addon.getLocalizedString(32908).encode('utf-8')
            elif key == 'Coin line/payphone':
                #name = '公衆電話'
                name = addon.getLocalizedString(32909).encode('utf-8')
        # 検索結果
        name = name or key or uri
        # 履歴に追加
        if history: self.history.append(uri, key, name)
        return name
