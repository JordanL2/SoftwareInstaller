#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class PacmanSource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+)\s+([^\s\,]+)[^\,]*\,(.+)$')
    description_regex = re.compile(r'^([^\:]+?)\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('pacman', 'Pacman')
        self.executor = CommandExecutor()

    def testinstalled(self):
        return self.executor.call('which pacman 2>/dev/null', None, None, True, None) != ''

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self.executor.call("pacman -Ss \"{0}\" | sed -e \"s/    //\" | paste -d, - -".format(name), self.search_regex, None, False)
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[2], row[1], installedids.get(row[0], '')))
        return results

    def local(self, name):
        if name is None:
            name = ''
        remoteresults = dict([(a.id, a) for a in self.search('') if a.installed != ''])
        results = []
        installedids = self._get_installed_ids()
        for id in installedids:
            app = None
            if id in remoteresults:
                app = remoteresults[id]
            else:
                app = self.getapp(id, installedids, True)
            if app is not None and (name is None or app.match(name)):
                results.append(app)
        return results

    def getapp(self, appid, installedids=None, skipremote=False):
        if installedids is None:
            installedids = self._get_installed_ids()

        desc = None
        version = None
        if not skipremote:
            table = self.executor.call("pacman -Si {0}".format(appid), self.description_regex, None, True, [0, 1])
            for row in table:
                if row[0] == 'Description':
                    desc = row[1]
                if row[0] == 'Version':
                    version = row[1]
        if version is None:
            version = '[Not Found]'
            table = self.executor.call("pacman -Qi {0}".format(appid), self.description_regex, None, True, [0, 1])
            for row in table:
                if row[0] == 'Description':
                    desc = row[1]
            if desc is None:
                return None
        return App(self, appid, appid, desc, version, installedids.get(appid, ''))

    def install(self, app):
        self.executor.call("pacman --noconfirm -S {0}".format(app.id))

    def remove(self, app):
        self.executor.call("pacman --noconfirm -R {0}".format(app.id))

    def update(self, apps, autoconfirm):
        #TODO
        print("Updating:", [a.id for a in apps])
        return None

    def _get_installed_ids(self):
        table = self.executor.call("pacman -Q", self.installed_regex)
        return dict([(row[0], row[1]) for row in table])
