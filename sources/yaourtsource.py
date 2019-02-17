#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class YaourtSource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+)\s+(\S+)\s+(\S+)\s+[^\,]+,(.+)$')
    description_regex = re.compile(r'^([^\:]+?)\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^local\/(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('yaourt', 'Yaourt')
        self.executor = CommandExecutor()

    def testinstalled(self):
        return self.executor.call('which yaourt 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        self.executor.call("yaourt -Sy")

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self.executor.call("yaourt -Ss \"{0}\" | sed -e \"s/    //\" | paste -d, - - | grep \"^aur/\"".format(name), self.search_regex, None, False, [0, 1])
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[3], row[1], installedids.get(row[0])))
        return results

    def local(self, name):
        installedids = self._get_installed_ids()
        results = []
        for appid in installedids.keys():
            app = self.getapp(appid, installedids)
            if name is None or app.match(name):
                results.append(app)
        return results

    def getapp(self, appid, installedids=None):
        if installedids is None:
            installedids = self._get_installed_ids()

        table = self.executor.call("yaourt -Si {0}".format(appid), self.description_regex, None, True, [0, 1])
        desc = None
        version = None
        for row in table:
            if row[0] == 'Description':
                desc = row[1]
            if row[0] == 'Version':
                version = row[1]
        if version is None:
            version = None
            table = self.executor.call("yaourt -Qi {0}".format(appid), self.description_regex, None, True, [0, 1])
            for row in table:
                if row[0] == 'Description':
                    desc = row[1]
            if desc is None:
                return None
        return App(self, appid, appid, desc, version, installedids.get(appid))

    def install(self, app):
        user = self.executor.getuser()
        self.executor.call("sudo -u {0} yaourt --noconfirm -S {1}".format(user, app.id))

    def remove(self, app):
        self.executor.call("yaourt --noconfirm -R {0}".format(app.id))

    def update(self, apps, autoconfirm):
        user = self.executor.getuser()
        for app in apps:
            self.executor.call("sudo -u {0} yaourt -S {1} --noconfirm".format(user, app.id))
        return None

    def _get_installed_ids(self):
        table = self.executor.call("yaourt -Q | grep \"^local/\"", self.installed_regex, None, False, [0, 1])
        return dict([(row[0], row[1]) for row in table])
