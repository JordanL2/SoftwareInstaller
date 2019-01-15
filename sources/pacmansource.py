#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re

class PacmanSource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+)\s+([^\s\,]+)[^\,]*\,(.+)$')
    description_regex = re.compile(r'^([^\:]+?)\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('pacman', 'Pacman')

    def testinstalled(self):
        return self._call('which pacman 2>/dev/null', None, None, True, None) != ''

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self._call("pacman -Ss \"{0}\" | sed -e \"s/    //\" | paste -d, - -".format(name), self.search_regex, None, False)
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[2], row[1], installedids.get(row[0], '')))
        return results

    def local(self, name):
        if name == None:
            name = ''
        results = [a for a in self.search(name) if a.installed != '']
        return results

    def getapp(self, appid):
        installedids = self._get_installed_ids()

        table = self._call("pacman -Si {0}".format(appid), self.description_regex, None, True)
        desc = ''
        version = ''
        for row in table:
            if row[0] == 'Description':
                desc = row[1]
            if row[0] == 'Version':
                version = row[1]
        return App(self, appid, appid, desc, version, installedids.get(appid, ''))

    def install(self, app):
        self._call("pacman --noconfirm -S {0}".format(app.id))

    def remove(self, app):
        self._call("pacman --noconfirm -R {0}".format(app.id))

    def _get_installed_ids(self):
        table = self._call("pacman -Q", self.installed_regex)
        return dict([(row[0], row[1]) for row in table])
