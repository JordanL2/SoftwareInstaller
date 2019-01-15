#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re

class YaourtSource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+)\s+(\S+)\s+(\S+)\s+[^\,]+,(.+)$')
    description_regex = re.compile(r'^([^\:]+?)\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^local\/(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('yaourt', 'Yaourt')

    def test_installed(self):
        return self.call('which yaourt 2>/dev/null') != ''

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self.call("yaourt -Ss \"{0}\" | sed -e \"s/    //\" | paste -d, - - | grep \"^aur/\" || true".format(name), self.search_regex, None, False)
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[3], row[1], installedids.get(row[0], '')))
        return results

    def local(self, name):
        installed = self._get_installed_ids()
        results = []
        for appid in installed.keys():
            app = self.getapp(appid)
            if name == None or (name.lower() in app.name.lower() or name.lower() in app.id.lower() or name.lower() in app.desc.lower()):
                results.append(app)
        return results

    def getapp(self, appid):
        installedids = self._get_installed_ids()

        table = self.call("yaourt -Si {0}".format(appid), self.description_regex, None, True)
        desc = ''
        version = ''
        for row in table:
            if row[0] == 'Description':
                desc = row[1]
            if row[0] == 'Version':
                version = row[1]
        return App(self, appid, appid, desc, version, installedids.get(appid, ''))

    def install(self, app):
        self.call("yaourt --noconfirm -S {0}".format(app.id))

    def remove(self, app):
        self.call("yaourt --noconfirm -R {0}".format(app.id))

    def _get_installed_ids(self):
        table = self.call("yaourt -Q | grep \"^local/\" || true", self.installed_regex)
        return dict([(row[0], row[1]) for row in table])
