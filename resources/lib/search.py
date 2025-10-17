# -*- coding: utf-8 -*-

import sys
import re

from resources.lib.common import Common

sys.path.append(Common.RESOURCES_PATH)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def search(key):
    try:
        # 番号案内ページのURL
        url = 'https://www.telnavi.jp/phone/%s' % key
        # ページ読み込み
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--disable-gpu')
        #opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
        opts.add_argument("--user-agent=Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=opts)
        driver.get(url)
        title = driver.title
        driver.quit()
        # スクレイピング
        # 電話番号08012000021の情報は？｜電話番号検索の電話帳ナビ
        # 電話番号0120102030は司法書士法人新宿事務所
        if re.match(r'電話番号[0-9]+は', title):
            name = re.sub(r'電話番号[0-9]+は', '', title)
        else:
            name = None
        Common.log('key=%s name=%s url=%s' % (key, name, url))
    except Exception as e:
        name = None
        Common.log(e)
    return name
