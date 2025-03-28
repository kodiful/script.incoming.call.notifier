# -*- coding: utf-8 -*-

import re

from urllib.request import urlopen
from bs4 import BeautifulSoup

from resources.lib.common import Common


def search(key):
    try:
        # 番号案内ページのURL
        url = 'https://www.telnavi.jp/phone/%s' % key
        # ページ読み込み
        res = urlopen(url)
        status = res.getcode()
        if status == 200:
            # タグ抽出
            html = res.read()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('title').get_text()
            # 電話番号08012000021の情報は？｜電話番号検索の電話帳ナビ
            # 電話番号0120102030は司法書士法人新宿事務所
            if re.match(r'電話番号[0-9]+は', title):
                name = re.sub(r'電話番号[0-9]+は', '', title)
            else:
                name = None
        else:
            name = None
        res.close()
        Common.log('key=%s name=%s status=%s url=%s' % (key, name, status, url))
    except Exception as e:
        name = None
        Common.log(e)
    return name
