# -*- coding: utf-8 -*-

import os

from resources.lib.commonmethods import Common as C


class Common(C):

    RESOURCES_PATH = os.path.join(C.PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH = os.path.join(DATA_PATH, 'image')
    PJSUA2_PATH = os.path.join(C.PLUGIN_PATH, 'resources', 'pjsua2')

    # スクリプトパス
    PY_FILE = os.path.join(PJSUA2_PATH, 'pjsua2.py')
    SO_FILE = os.path.join(PJSUA2_PATH, '_pjsua2.so')

    # ファイルパス
    HISTORY_FILE = os.path.join(C.PROFILE_PATH, 'history.json')
    PHONEBOOK_FILE = os.path.join(C.PROFILE_PATH, 'phonebook.json')
    CACHE_FILE = os.path.join(C.PROFILE_PATH, 'cache.json')

    # サムネイル
    CONTACTS = os.path.join(IMAGE_PATH, 'icons8-contacts-filled-500.png')
    RINGER_VOLUME = os.path.join(IMAGE_PATH, 'icons8-ringer-volume-filled-500.png')
