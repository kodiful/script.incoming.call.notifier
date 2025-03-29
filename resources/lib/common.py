# -*- coding: utf-8 -*-

import os
import inspect
import calendar

import xbmc
import xbmcaddon
import xbmcvfs


class Common:

    # アドオンオブジェクト
    ADDON = xbmcaddon.Addon()

    # アドオン属性
    INFO = ADDON.getAddonInfo
    ADDON_ID = INFO('id')
    ADDON_NAME = INFO('name')

    # ファイル/ディレクトリ
    PROFILE_PATH = xbmcvfs.translatePath(INFO('profile'))
    PLUGIN_PATH = xbmcvfs.translatePath(INFO('path'))
    RESOURCES_PATH = os.path.join(PLUGIN_PATH, 'resources')
    DATA_PATH = os.path.join(RESOURCES_PATH, 'data')
    IMAGE_PATH = os.path.join(DATA_PATH, 'image')

    # アドオン設定へのアクセス
    STR = ADDON.getLocalizedString
    GET = ADDON.getSetting
    SET = ADDON.setSetting

    # スクリプトパス
    PJSUA2_PATH = os.path.join(RESOURCES_PATH, 'pjsua2')
    PY_FILE = os.path.join(PJSUA2_PATH, 'pjsua2.py')
    SO_FILE = os.path.join(PJSUA2_PATH, '_pjsua2.so')

    # DBファイルパス
    DB_PATH = os.path.join(PROFILE_PATH, 'phone.db')

    # サムネイル
    CONTACTS = os.path.join(IMAGE_PATH, 'icons8-contacts-filled-500.png')
    RINGER_VOLUME = os.path.join(IMAGE_PATH, 'icons8-ringer-volume-filled-500.png')

    # 通知
    @staticmethod
    def notify(message, **options):
        # ポップアップする時間
        time = options.get('time', 10000)
        # ポップアップアイコン
        image = options.get('image')
        if image:
            pass
        elif options.get('error', False):
            image = 'DefaultIconError.png'
        else:
            image = 'DefaultIconInfo.png'
        # ログ出力
        Common.log(message, error=options.get('error', False))
        # ポップアップ通知
        xbmc.executebuiltin('Notification("%s","%s",%d,"%s")' % (Common.ADDON_NAME, message, time, image))

    # ログ出力
    @staticmethod
    def log(*messages, **options):
        # ログレベルを設定
        if options.get('error', False):
            level = xbmc.LOGERROR
        elif options.get('notice', False):
            level = xbmc.LOGINFO
        elif Common.GET('debug') == 'true':
            level = xbmc.LOGINFO
        else:
            level = None
        # ログ出力
        if level:
            frame = inspect.currentframe().f_back
            xbmc.log('%s: %s(%d): %s: %s' % (
                Common.ADDON_ID,
                os.path.basename(frame.f_code.co_filename),
                frame.f_lineno,
                frame.f_code.co_name,
                ' '.join(map(lambda x: str(x), messages))
            ), level)

    @staticmethod
    def weekday(datetime_str):
        # 2023-04-20 05:00:00 -> calendar.weekday(2023, 4, 20) -> 3
        date, _ = datetime_str.split(' ')
        year, month, day = map(int, date.split('-'))
        return calendar.weekday(year, month, day)

    # workaround for encode problems for strftime on Windows
    # cf. https://ja.stackoverflow.com/questions/44597/windows上のpythonのdatetime-strftimeで日本語を使うとエラーになる
    @staticmethod
    def strftime(d, format):
        return d.strftime(format.encode('unicode-escape').decode()).encode().decode('unicode-escape')
