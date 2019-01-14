#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re

class PacmanSource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+) [^\,]+\,(.+)$')
    description_regex = re.compile(r'^Description\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('pacman', 'Pacman')

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self.call("pacman -Ss {0} | sed -e \"s/    //\" | paste -d, - -".format(name), self.search_regex, None, False)
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[1], row[0] in installedids))
        return results

    def getapp(self, appid):
        installedids = self._get_installed_ids()

        table = self.call("pacman -Si {0} | grep '^Description'".format(appid), self.description_regex)
        desc = table[0][0]
        return App(self, appid, appid, desc, appid in installedids)

    def install(self, app):
        self.call("pacman --noconfirm -S {0}".format(app.id))

    def remove(self, app):
        self.call("pacman --noconfirm -R {0}".format(app.id))

    def _get_installed_ids(self):
        table = self.call("pacman -Q", self.installed_regex)
        return [row[0] for row in table]
