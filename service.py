# -*- coding: utf-8 -*-

import sys
import os
import glob
import shutil
import urllib
import xbmc
import xbmcaddon

from resources.lib.common import Common
from resources.lib.lookup import lookup

# pjsua2.pyのパス設定を取得
srcfile = Common.GET('pjsua2')
# 設定をチェック
if not os.path.isfile(srcfile) or os.path.basename(srcfile) != 'pjsua2.py':
    Common.ADDON.openSettings()
    sys.exit()
try:
    # pjsua2.pyをコピー
    shutil.copy(srcfile, Common.PY_FILE)
    # _pjsua2.soをコピー
    srcfile = glob.glob(os.path.join(os.path.dirname(srcfile), '_pjsua2*.so'))[0]
    shutil.copy(srcfile, Common.SO_FILE)
    # インポート実行
    from resources.pjsua2 import pjsua2 as pj
except Exception as e:
    Common.notify('Importing pjsua2 failed', time=3000, error=True)
    Common.log(e)
    sys.exit()

# 電子メールクライアントの有無を確認
try:
    mailaddon = 'script.handler.email'
    xbmcaddon.Addon(mailaddon)
    Common.SET('mailaddon', mailaddon)
except Exception:
    Common.SET('mailaddon', '')

# LINE Notifyハンドラの有無を確認
try:
    lineaddon = 'script.handler.line.notify'
    xbmcaddon.Addon(lineaddon)
    Common.SET('lineaddon', lineaddon)
except Exception:
    Common.SET('lineaddon', '')


class Monitor(xbmc.Monitor):

    interval = 1

    def __init__(self, *args, **kwargs):
        super().__init__()

    def onSettingsChanged(self):
        Common.log('settings changed')

    def onScreensaverActivated(self):
        Common.log('screensaver activated')

    def onScreensaverDeactivated(self):
        Common.log('screensaver deactivated')


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
        # 通知
        duration = Common.GET('duration')
        Common.notify(name, time=int(duration) * 1000)
        # メールによる通知
        if Common.GET('mailaddon') and Common.GET('mailnotify') == 'true':
            template = Common.GET('mailtemplate') or Common.STR(32913)
            address = Common.GET('mailaddress')
            message = template.format(name=name, key=key, uri=uri)
            values = {'action': 'send', 'subject': message, 'message': message, 'to': address}
            postdata = urllib.urlencode(values)
            xbmc.executebuiltin('RunPlugin("plugin://%s?%s")' % (mailaddon, postdata))
        # LINE notifyによる通知
        if Common.GET('lineaddon') and Common.GET('linenotify') == 'true':
            template = Common.GET('linetemplate') or Common.STR(32913)
            token = Common.GET('linetoken')
            message = template.format(name=name, key=key, uri=uri)
            values = {'action': 'send', 'name': token, 'message': message}
            postdata = urllib.urlencode(values)
            xbmc.executebuiltin('RunPlugin("plugin://%s?%s")' % (lineaddon, postdata))


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
    monitor = Monitor()
    while not monitor.abortRequested():
        # check abortion
        if monitor.waitForAbort(monitor.interval):
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
