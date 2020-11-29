# -*- coding: utf-8 -*-

import os
import xbmc, xbmcaddon

class Const:

    # ガラポンTVクライアント
    ADDON = xbmcaddon.Addon()
    ADDON_ID = ADDON.getAddonInfo('id')
    ADDON_NAME= ADDON.getAddonInfo('name')

    GET = ADDON.getSetting
    SET = ADDON.setSetting
    #STR = ADDON.getLocalizedString
    @staticmethod
    def STR(id): return Const.ADDON.getLocalizedString(id).encode('utf-8')

    # ディレクトリパス
    PROFILE_PATH   = xbmc.translatePath(ADDON.getAddonInfo('profile'))
    PLUGIN_PATH    = xbmc.translatePath(ADDON.getAddonInfo('path'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    DATA_PATH      = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH     = os.path.join(DATA_PATH, 'image')

    # ファイルパス
    HISTORY_FILE   = os.path.join(PROFILE_PATH, 'history.json')
    PHONEBOOK_FILE = os.path.join(PROFILE_PATH, 'phonebook.json')
    CACHE_FILE     = os.path.join(PROFILE_PATH, 'cache.json')

    # サムネイル
    CONTACTS       = os.path.join(IMAGE_PATH, 'icons8-contacts-filled-500.png')
    RINGER_VOLUME  = os.path.join(IMAGE_PATH, 'icons8-ringer-volume-filled-500.png')
