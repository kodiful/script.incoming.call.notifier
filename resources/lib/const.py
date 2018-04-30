# -*- coding: utf-8 -*-

import os
import xbmc, xbmcaddon

class Const:

    # ガラポンTVクライアント
    ADDON = xbmcaddon.Addon()
    ADDON_ID = ADDON.getAddonInfo('id')

    STR = ADDON.getLocalizedString
    GET = ADDON.getSetting
    SET = ADDON.setSetting

    # ディレクトリパス
    PROFILE_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile').decode('utf-8'))
    PLUGIN_PATH = xbmc.translatePath(ADDON.getAddonInfo('path').decode('utf-8'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH = os.path.join(DATA_PATH, 'image')

    # サムネイル
    CONTACTS      = os.path.join(IMAGE_PATH, 'icons8-contacts-filled-500.png')
    RINGER_VOLUME = os.path.join(IMAGE_PATH, 'icons8-ringer-volume-filled-500.png')
