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
            name = re.sub(r'電話番号[0-9]+は', '', title)
        else:
            name = None
        res.close()
        Common.log('key=%s name=%s status=%s url=%s' % (key, name, status, url))
    except Exception as e:
        name = None
        Common.log(e)
    return name
