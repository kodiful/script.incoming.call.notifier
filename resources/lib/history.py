# -*- coding: utf-8 -*-

import os, json
import datetime
import xbmc, xbmcaddon

from common import log
from const import Const

#-------------------------------------------------------------------------------
class History:

    filepath = None
    data = None

    def __init__(self, filename):
        self.filename = filename
        self.filepath = os.path.join(Const.PROFILE_PATH, filename)
        self.read()

    def read(self):
        if os.path.isfile(self.filepath):
            try:
                f = open(self.filepath,'r')
                self.data = json.loads(f.read(), 'utf-8')
                f.close()
            except ValueError:
                log('broken json: %s' % self.filepath)
                self.data = []
        else:
            self.data = []

    def write(self):
        f = open(self.filepath,'w')
        f.write(json.dumps(self.data, sort_keys=True, ensure_ascii=False, indent=2).encode('utf-8'))
        f.close()

    def append(self, uri, key, name):
        if isinstance(uri, str): url = uri.decode('utf-8')
        if isinstance(key, str): key = key.decode('utf-8')
        if isinstance(name, str): name = name.decode('utf-8')
        data = {}
        now = datetime.datetime.now()
        data['date'] = now.strftime('%Y-%m-%d')
        data['time'] = now.strftime('%H:%M:%S')
        data['weekday'] = now.weekday()
        data['uri'] = uri
        data['key'] = key
        data['name'] = name
        self.data.append(data)
        self.write()

    def clear(self):
        if os.path.isfile(self.filepath):
            os.remove(self.filepath)
        self.data = []
        self.write()
