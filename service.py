# -*- coding: utf-8 -*-

import sys
import os
import urllib
import threading
import xbmc, xbmcaddon

from resources.lib.common import *
from resources.lib.lookup import lookup
from resources.lib.const import Const

# pjsuaのパスをチェック
path = Const.GET('pjsua')
if path == '':
    message = 'Can\'t import pjsua'
    xbmc.executebuiltin('Notification("%s","%s",3000,"DefaultIconError.png")' % (Const.ADDON_NAME,message))
    sys.exit()

# pjsuaをインポート
sys.path.append(os.path.dirname(path))
try:
    import pjsua as pj
except:
    message = 'Can\'t import pjsua'
    xbmc.executebuiltin('Notification("%s","%s",3000,"DefaultIconError.png")' % (Const.ADDON_NAME,message))
    sys.exit()

# メールアドオンの有無を確認
try:
    mailaddon = 'script.handler.email'
    xbmcaddon.Addon(mailaddon)
    Const.SET('mailaddon', mailaddon)
except:
    Const.SET('mailaddon', '')

# LINE Notifyアドオンの有無を確認
try:
    lineaddon = 'script.handler.line.notify'
    xbmcaddon.Addon(lineaddon)
    Const.SET('lineaddon', lineaddon)
except:
    Const.SET('lineaddon', '')


class Monitor(xbmc.Monitor):

    interval = 1

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onSettingsChanged(self):
        log('settings changed')

    def onScreensaverActivated(self):
        log('screensaver activated')

    def onScreensaverDeactivated(self):
        log('screensaver deactivated')


class MyCallback(pj.AccountCallback):

    sem = None

    def __init__(self, account=None):
        pj.AccountCallback.__init__(self, account)

    def wait(self):
        '''
        セマフォは release() を呼び出した数から acquire() を呼び出した数を引き、初期値を足した値=カウンタを管理します。
        acquire() は、カウンタがゼロになっている場合、他のスレッドが release() を呼び出すまでブロックします。
        '''
        self.sem = threading.Semaphore(0)
        self.sem.acquire()

    def on_reg_state(self):
        if self.sem:
            if self.account.info().reg_status >= 200:
                self.sem.release()
        # ログ
        info = self.account.info()
        log("\n".join([
            "Registration complete",
            "uri: %s" % info.uri,
            "reg_active: %s" % info.reg_active,
            "reg_expires: %s" % info.reg_expires,
            "reg_status: %s" % info.reg_status,
            "reg_reason: %s" % info.reg_reason,
            "online_status: %s" % info.online_status,
            "online_text: %s" % info.online_text
        ]))

        '''
        1xx = 情報応答
        100 試行中
        180 呼び出し中
        181 転送中
        182 順番待ち
        183 セッション進行中

        2xx = 成功応答
        200 OK
        202 受諾：照会に使用

        3xx = リダイレクト応答
        300 複数の転送先
        301 永久的に移動
        302 一時的に移動
        305 プロキシ使用
        380 ほかのサービス

        4xx = リクエスト エラー
        400 不正なリクエスト
        401 認証が必要：レジストラのみ利用可。プロキシは「プロキシ認証 407」が必要
        402 支払いが必要（将来使われる可能性あり）
        403 禁止
        404 見つかりません：ユーザが見つかりません
        405 メソッド利用不可
        406 容認不可
        407 プロキシ認証が必要
        408 リクエスト タイムアウト：時間内にユーザが見つかりませんでした
        410 不在：ユーザは過去に存在しましたが、もうここにはいません
        413 リクエスト本体が大きすぎます
        414 リクエストURIが大きすぎます
        415 非対応メディア
        416 非対応URIスキーム
        420 不正な拡張：ＳＩＰプロトコル拡張がサーバに認識されません
        421 拡張が必要
        423 間隔が短すぎます
        480 一時的に利用不可
        481 通話 / トランザクションが存在しません
        482 ループ検出
        483 最大ホップ数超過
        484 不完全なアドレス
        485 あいまい
        486 話し中
        487 リクエストが中止
        488 ここでは容認不可
        491 リクエスト待機中
        493 解読不可：S/MIME本文を解読できませんでした

        5xx = サーバー エラー
        500 サーバ内部エラー
        501 非実装：SIPリクエスト メソッドが実装されていません
        502 不正なゲートウェイ
        503 サービス利用不可
        504 サーバタイムアウト
        505 バージョン非対応：サーバはこのSIPバージョンに対応していません
        513 メッセージが大きすぎます

        6xx = グローバル エラー
        600 随所で話し中
        603 拒否
        604 どこにも存在しません
        606 容認不可
        '''

    def on_incoming_call(self, call):
        # ログ
        info = call.info()
        log("\n".join([
            "Incoming call",
            "uri: %s" % info.uri,
            "contact: %s" % info.contact,
            "remote_uri: %s" % info.remote_uri,
            "remote_contact: %s" % info.remote_contact,
            "sip_call_id: %s" % info.sip_call_id,
            "state_text: %s" % info.state_text,
            "sip_call_id: %s" % info.sip_call_id,
            "last_code: %s" % info.last_code,
            "call_time: %s" % info.call_time,
            "total_time: %s" % info.total_time
        ]))
        # Kodiをアクティベート
        if Const.GET('cec') == 'true':
            xbmc.executebuiltin('CECActivateSource')
        # 発信者番号
        uri = call.info().remote_uri
        # 番号検索
        name, key = lookup(uri)
        # 通知
        duration = Const.GET('duration')
        notify(name, time=int(duration)*1000)
        # メールによる通知
        if Const.GET('mailaddon') and Const.GET('mailnotify') == 'true':
            template = Const.GET('mailtemplate') or Const.STR(32913)
            address = Const.GET('mailaddress')
            message = template.format(name=name,key=key,uri=uri)
            values = {'action':'send', 'subject':message, 'message':message, 'to':address}
            postdata = urllib.urlencode(values)
            xbmc.executebuiltin('RunPlugin("plugin://%s?%s")' % (mailaddon,postdata))
        # LINE notifyによる通知
        if Const.GET('lineaddon') and Const.GET('linenotify') == 'true':
            template = Const.GET('linetemplate') or Const.STR(32913)
            token = Const.GET('linetoken')
            message = template.format(name=name,key=key,uri=uri)
            values = {'action':'send', 'name':token, 'message':message}
            postdata = urllib.urlencode(values)
            xbmc.executebuiltin('RunPlugin("plugin://%s?%s")' % (lineaddon,postdata))


def register(lib):

    try:
        # settings
        port = Const.GET('port')
        extension = Const.GET('extension')
        domain = Const.GET('domain')
        realm = Const.GET('realm')
        username = Const.GET('username')
        password = Const.GET('password')

        lib.init()
        lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(int(port)))
        lib.start()

        acc_conf = pj.AccountConfig()
        acc_conf.id = "sip:%s@%s" % (extension, domain)
        acc_conf.reg_uri = "sip:%s" % (domain)
        if realm and username and password:
            acc_conf.auth_cred.append(pj.AuthCred(realm, username, password))
        acc = lib.create_account(acc_conf)

        acc_cb = MyCallback(acc)
        acc.set_callback(acc_cb)
        acc_cb.wait()

        return acc

    except Exception as e:
        log(e, error=True)
        lib.destroy()
        lib = None


if __name__ == "__main__":

    try:
        lib = pj.Lib()
        acc = register(lib)
        status = acc.info().reg_status
        if status == 200:
            notify('Registered as SIP client', time=3000)
            # monitor loop
            monitor = Monitor()
            while not monitor.abortRequested():
                if monitor.waitForAbort(monitor.interval):
                    break
                if acc.info().reg_expires < 0:
                    acc.set_registration(True)
        else:
            notify('SIP registration failed (%d)' % status, time=3000)
        lib.destroy()
        lib = None

    except Exception as e:
        log(e, error=True)
        lib.destroy()
        lib = None
