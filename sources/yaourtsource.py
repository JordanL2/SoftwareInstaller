#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re


class YaourtSource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+)\s+(\S+)\s+(\S+)\s+[^\,]+,(.+)$')
    description_regex = re.compile(r'^([^\:]+?)\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^local\/(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('yaourt', 'Yaourt')

    def testinstalled(self):
        return self._call('which yaourt 2>/dev/null', None, None, True, None) != ''

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self._call("yaourt -Ss \"{0}\" | sed -e \"s/    //\" | paste -d, - - | grep \"^aur/\"".format(name), self.search_regex, None, False, [0, 1])
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[3], row[1], installedids.get(row[0], '')))
        return results

    def local(self, name):
        installedids = self._get_installed_ids()
        results = []
        for appid in installedids.keys():
            app = self.getapp(appid, installedids)
            if name == None or app.match(name):
                results.append(app)
        return results

    #TODO this throws exception if appid not found
    def getapp(self, appid, installedids=None):
        if installedids == None:
            installedids = self._get_installed_ids()

        table = self._call("yaourt -Si {0}".format(appid), self.description_regex, None, True)
        desc = None
        version = None
        for row in table:
            if row[0] == 'Description':
                desc = row[1]
            if row[0] == 'Version':
                version = row[1]
        if version == None:
            version = '[Not Found]'
            table = self._call("yaourt -Qi {0}".format(appid), self.description_regex, None, True)
            for row in table:
                if row[0] == 'Description':
                    desc = row[1]
        return App(self, appid, appid, desc, version, installedids.get(appid, ''))

    def install(self, app):
        self._call("yaourt --noconfirm -S {0}".format(app.id))

    def remove(self, app):
        self._call("yaourt --noconfirm -R {0}".format(app.id))

    def update(self, apps, autoconfirm):
        #TODO
        print("Updating:", [a.id for a in apps])
        return None

    def _get_installed_ids(self):
        table = self._call("yaourt -Q | grep \"^local/\"", self.installed_regex, None, False, [0, 1])
        return dict([(row[0], row[1]) for row in table])
