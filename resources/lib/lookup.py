# -*- coding: utf-8 -*-

import sys
import os
import re

from resources.lib.common import Common
from resources.lib.phonebook import PhoneBook
from resources.lib.history import History
from resources.lib.defaultsearch import search


# searchをインポート
path = Common.GET('customsearch')
if os.path.isfile(path):
    dirname = os.path.dirname(path)
    if os.path.samefile(path, os.path.join(dirname, 'customsearch.py')):
        sys.path.append(os.path.dirname(path))
        from customsearch import search


def lookup(uri, cache=True, history=True):
    name = None
    key = None
    m = re.compile(r'(?:"(.*)"|(.*))\s*<(sip:(.*)@.*|.*)>').search(uri)
    if m:
        key = m.group(1) or m.group(2) or m.group(4) or m.group(3)
        # 0で始まって9桁以上ある場合は電話番号として先ず電話帳、次にキャッシュ、最後にウェブを検索
        if re.compile('^0[0-9]{8,}').search(key):
            # 電話帳を検索
            name = PhoneBook().lookup(key)
            if name is None:
                # キャッシュを検索
                cache = PhoneBook(Common.CACHE_FILE)
                name = cache.lookup(key)
                if name is None:
                    # ウェブを検索
                    name = search(key)
                    if name:
                        # キャッシュに追加
                        cache.update(key, name or 'n/a')
                elif name == 'n/a':
                    name = None
        # 以下は
        # http://www.ttc.or.jp/jp/document_list/pdf/j/STD/JJ-90.22v1.1.pdf
        # による
        elif key == 'Anonymous':
            # ユーザ拒否のため通知不可
            name = Common.STR(32908)
        elif key == 'Coin line/payphone':
            # 公衆電話発信のため通知不可
            name = Common.STR(32909)
        elif key == 'Unavailable':
            # 通知可能な情報が存在しない
            name = Common.STR(32910)
        elif key == 'Interaction with other service':
            # サービス競合のため通知不可
            name = Common.STR(32910)
    # 検索結果
    name = name or key or uri
    # 履歴に追加
    History().append(uri, key or 'n/a', name or 'n/a')
    return name, key
