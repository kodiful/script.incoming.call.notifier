# -*- coding: utf-8 -*-

import sys, os, re
import urllib

import xbmc, xbmcaddon

from phonebook import PhoneBook
from history import History

from common import log

# searchをインポート
addon = xbmcaddon.Addon()
path = addon.getSetting('search')
if os.path.isfile(path):
    dirname = os.path.dirname(path)
    if os.path.samefile(path, os.path.join(dirname,'customsearch.py')):
        sys.path.append(os.path.dirname(path))
        from customsearch import search
    else:
        from defaultsearch import search
else:
    from defaultsearch import search

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
        m = re.compile('(?:"(.*)"|(.*))\s*<(sip:(.*)@.*|.*)>').search(uri)
        if m:
            key = m.group(1) or m.group(2) or m.group(4) or m.group(3)
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
                        if cache: self.cache.update(key, name or 'n/a')
                    elif name == 'n/a':
                        name = None
            # 以下は
            # http://www.ttc.or.jp/jp/document_list/pdf/j/STD/JJ-90.22v1.1.pdf
            # による
            elif key == 'Anonymous':
                # ユーザ拒否のため通知不可
                name = addon.getLocalizedString(32908).encode('utf-8')
            elif key == 'Coin line/payphone':
                # 公衆電話発信のため通知不可
                name = addon.getLocalizedString(32909).encode('utf-8')
            elif key == 'Unavailable':
                # 通知可能な情報が存在しない
                name = addon.getLocalizedString(32910).encode('utf-8')
            elif key == 'Interaction with other service':
                # サービス競合のため通知不可
                name = addon.getLocalizedString(32910).encode('utf-8')
        # 検索結果
        name = name or key or uri
        # 履歴に追加
        if history: self.history.append(uri, key or 'n/a', name or 'n/a')
        return name, key
