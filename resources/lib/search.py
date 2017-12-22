# -*- coding: utf-8 -*-

import urllib
from bs4 import BeautifulSoup
from common import log

def search(key):
    try:
        # 番号案内ページのURL
        url = 'https://www.telnavi.jp/phone/%s' % key
        # ページ読み込み
        res = urllib.urlopen(url)
        status = res.getcode()
        if status == 200:
            # タグ抽出
            html = res.read()
            soup = BeautifulSoup(html, 'html.parser')
            name = soup.find('td',{'itemprop':'name'}).get_text().strip()
        else:
            name = None
        res.close()
        log('key=%s name=%s status=%s url=%s' % (key, name, status, url))
    except Exception as e:
        name = None
        log(e)
    return name
