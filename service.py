# -*- coding: utf-8 -*-

import sys
import os
import glob
import shutil
import json
import xbmc
import xbmcaddon

from urllib.parse import urlencode

from resources.lib.common import Common
from resources.lib.db import DB
from resources.lib.lookup import parse
from resources.lib.lookup import lookup

# pjsua2.pyのパス設定を取得
path = Common.GET('pjsua2')
# 設定をチェック
if os.path.isfile(path) and os.path.basename(path) == 'pjsua2.py':
    pass
else:
    Common.ADDON.openSettings()
    sys.exit()

# pjsua2をインポート
try:
    # コピー先のディレクトリを用
    dir = os.path.dirname(Common.PY_FILE)
    os.makedirs(dir, exist_ok=True)
    # pjsua2.pyをコピー
    shutil.copy(path, Common.PY_FILE)
    # _pjsua2.soをコピー
    path = glob.glob(os.path.join(os.path.dirname(path), '_pjsua2*.so'))[0]
    shutil.copy(path, Common.SO_FILE)
    # インポート実行
    from resources.pjsua2 import pjsua2 as pj
except Exception as e:
    Common.notify('Importing pjsua2 failed', time=3000, error=True)
    Common.log(e)
    sys.exit()

# 旧形式のデータをインポート
if os.path.exists(Common.DB_PATH) is False:
    # 旧形式のjsonファイルからインポート
    db = DB()
    # 旧形式のjsonファイルのバックアップ先
    backupdir = os.path.join(Common.PROFILE_PATH, '~backup')
    os.makedirs(backupdir, exist_ok=True)
    # cache
    json_file = os.path.join(Common.PROFILE_PATH, 'cache.json')
    if os.path.exists(json_file):
        with open(json_file, encoding='utf-8') as f:
            for key, name in json.loads(f.read()).items():
                db.add_to_cache(key, name)
        shutil.move(json_file, backupdir)
    # phonebook
    json_file = os.path.join(Common.PROFILE_PATH, 'phonebook.json')
    if os.path.exists(json_file):
        with open(json_file, encoding='utf-8') as f:
            for key, name in json.loads(f.read()).items():
                db.add_to_phonebook(key, name)
        shutil.move(json_file, backupdir)
    # history
    json_file = os.path.join(Common.PROFILE_PATH, 'history.json')
    if os.path.exists(json_file):
        with open(json_file, encoding='utf-8') as f:
            for item in json.loads(f.read()):
                db.add_to_history(f"{item['date']} {item['time']}", item['key'], item['name'], item['uri'])
        shutil.move(json_file, backupdir)
    # holidaysテーブル作成
    json_file = os.path.join(Common.DATA_PATH, 'json', 'holidays.json')
    with open(json_file, encoding='utf-8') as f:
        for data in json.loads(f.read()):
            db.add_holiday(data)
    # インポート完了
    db.conn.close()


class Account(pj.Account):

    def __init__(self):
        super().__init__()

    def onRegState(self, param):
        # ログ
        Common.log('\n'.join([
            # https://www.pjsip.org/pjsip/docs/html/structpj_1_1OnRegStateParam.htm
            'status: %s' % param.status,
            'code: %s' % param.code,
            'reason: %s' % param.reason,
            # 'rdata: %s' % param.rdata,
            'rdata.info: %s' % param.rdata.info,
            'rdata.wholeMsg: \n-----\n%s\n-----' % '\n'.join(param.rdata.wholeMsg.strip().split('\r\n')),
            'rdata.srcAddress: %s' % param.rdata.srcAddress,
            'rdata.pjRxData: %s' % param.rdata.pjRxData,
            'expiration: %s' % param.expiration,
        ]))
        info = self.getInfo()
        Common.log('\n'.join([
            # https://www.pjsip.org/pjsip/docs/html/structpj_1_1AccountInfo.htm
            'id: %s' % info.id,
            'isDefault: %s' % info,
            'uri: %s' % info.uri,
            'regIsConfigured: %s' % info.regIsConfigured,
            'regIsActive: %s' % info.regIsActive,
            'regExpiresSec: %s' % info.regExpiresSec,
            'regStatus: %s' % info.regStatus,
            'regStatusText: %s' % info.regStatusText,
            'regLastErr: %s' % info.regLastErr,
            'onlineStatus: %s' % info.onlineStatus,
            'onlineStatusText: %s' % info.onlineStatusText,
        ]))
        # 通知
        if param.code == 200:
            Common.notify('Registered as SIP client', time=3000)
        else:
            Common.notify('SIP registration failed (%d)' % param.code, time=3000, error=True)

    def onIncomingCall(self, param):
        # ログ
        Common.log('\n'.join([
            # https://www.pjsip.org/pjsip/docs/html/structpj_1_1OnIncomingCallParam.htm
            'callId: %s' % param.callId,
            # 'rdata: %s' % param.rdata,
            'rdata.info: %s' % param.rdata.info,
            'rdata.wholeMsg: \n-----\n%s\n-----' % '\n'.join(param.rdata.wholeMsg.strip().split('\r\n')),
            'rdata.srcAddress: %s' % param.rdata.srcAddress,
            'rdata.pjRxData: %s' % param.rdata.pjRxData,
        ]))
        call = pj.Call(self, param.callId)
        info = call.getInfo()
        Common.log('\n'.join([
            # https://www.pjsip.org/pjsip/docs/html/structpj_1_1CallInfo.htm
            'id: %s' % info.id,
            'role: %s' % info.role,
            'accId: %s' % info.accId,
            'localUri: %s' % info.localUri,
            'localContact: %s' % info.localContact,
            'remoteUri: %s' % info.remoteUri,
            'remoteContact: %s' % info.remoteContact,
            'callIdString: %s' % info.callIdString,
            # 'setting: %s' % info.setting,
            'setting.flag: %s' % info.setting.flag,
            'setting.reqKeyframeMethod: %s' % info.setting.reqKeyframeMethod,
            'setting.audioCount: %s' % info.setting.audioCount,
            'setting.videoCount: %s' % info.setting.videoCount,
            'state: %s' % info.state,
            'stateText: %s' % info.stateText,
            'lastStatusCode: %s' % info.lastStatusCode,
            'media: %s' % info.media,
            'provMedia: %s' % info.provMedia,
            'connectDuration: %d.%03d' % (info.connectDuration.sec, info.connectDuration.msec),
            'totalDuration: %d.%03d' % (info.totalDuration.sec, info.totalDuration.msec),
            'remOfferer: %s' % info.remOfferer,
            'remAudioCount: %s' % info.remAudioCount,
            'remVideoCount: %s' % info.remVideoCount,
        ]))
        # Kodiをアクティベート
        if Common.GET('cec') == 'true':
            xbmc.executebuiltin('CECActivateSource')
        # 発信者番号から番号検索
        name, key = lookup(info.remoteUri)
        local = parse(info.localUri)
        # ディスプレイに通知
        Common.notify(name, time=3000)
        xbmc.executebuiltin('Container.Refresh')
        # 外部アドオンに通知
        notifier = Common.GET('notifier')
        if notifier:
            try:
                xbmcaddon.Addon(notifier)
                template = Common.STR(32913)  # "{name}<{key}>から<{local}>に着信がありました"
                message = template.format(name=name, key=key, local=local)
                xbmc.executebuiltin('RunPlugin("plugin://%s?%s")' % (notifier, urlencode({
                    'addon': Common.ADDON_NAME,
                    'message': message
                })))
            except Exception:
                Common.log('Notifier error', error=True)


if __name__ == '__main__':

    # settings
    port = Common.GET('port')
    extension = Common.GET('extension')
    domain = Common.GET('domain')
    realm = Common.GET('realm')
    username = Common.GET('username')
    password = Common.GET('password')

    # create and initialize the library
    ep_cfg = pj.EpConfig()
    ep_cfg.uaConfig.threadCnt = 0  # Python does not like PJSUA2's thread. It will result in segmentation fault
    ep_cfg.uaConfig.mainThreadOnly = True
    ep = pj.Endpoint()
    ep.libCreate()
    ep.libInit(ep_cfg)

    # create SIP transport
    tp_cfg = pj.TransportConfig()
    tp_cfg.port = int(port)
    ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)

    # start the library
    ep.libStart()

    # account configuration
    ac_cfg = pj.AccountConfig()
    ac_cfg.idUri = 'sip:%s@%s' % (extension, domain)
    ac_cfg.regConfig.registrarUri = 'sip:%s' % (domain)
    if realm and username and password:
        cred = pj.AuthCredInfo('digest', realm, username, 0, password)
        ac_cfg.sipConfig.authCreds.append(cred)

    # create the account
    ac = Account()
    ac.create(ac_cfg)

    # monitor loop
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        # check abortion
        if monitor.waitForAbort(1):
            break
        # check status
        if ac.getInfo().regStatus > 200:
            break
        # check expiration
        if ac.getInfo().regExpiresSec < 0:
            ac.setRegistration(True)
        # handle events
        status = ep.libHandleEvents(10)
        if status < 0:
            Common.notify('SIP event handler failed (%d)' % status, time=3000, error=True)

    # shutdown the account
    ac.shutdown()

    # destroy the library
    ep.libDestroy()
