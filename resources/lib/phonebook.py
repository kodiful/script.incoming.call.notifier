# -*- coding: utf-8 -*-

import os, json
import xbmc, xbmcaddon

from common import log

#-------------------------------------------------------------------------------
class PhoneBook:

    filepath = None
    data = None

    def __init__(self, filename):
        addon = xbmcaddon.Addon()
        profile = xbmc.translatePath(addon.getAddonInfo('profile'))
        self.filename = filename
        self.filepath = os.path.join(profile, filename)
        self.read()

    def read(self):
        if os.path.isfile(self.filepath):
            try:
                f = open(self.filepath,'r')
                self.data = json.loads(f.read(), 'utf-8')
                f.close()
            except ValueError:
                log('broken json: %s' % self.filepath)
                self.data = {}
        else:
            self.data = {}

    def write(self):
        f = open(self.filepath,'w')
        f.write(json.dumps(self.data, sort_keys=True, ensure_ascii=False, indent=2).encode('utf-8'))
        f.close()

    def lookup(self, key=None):
        if isinstance(key, str): key = key.decode('utf-8')
        try:
            if key:
                name = self.data[key].encode('utf-8')
            else:
                name = None
        except KeyError:
            name = None
        return name

    def update(self, key=None, name=None):
        if isinstance(key, str): key = key.decode('utf-8')
        if isinstance(name, str): name = name.decode('utf-8')
        if key and name:
            self.data[key] = name
            self.write()

    def remove(self, key=None, name=None):
        if isinstance(key, str): key = key.decode('utf-8')
        if isinstance(name, str): name = name.decode('utf-8')
        if key and name and self.data[key] == name:
            self.data.pop(key)
            self.write()

    def clear(self):
        if os.path.isfile(self.filepath):
            os.remove(self.filepath)
        self.data = {}
