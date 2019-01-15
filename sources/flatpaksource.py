#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re

class FlatpakSource(AbstractSource):

    search_regex = re.compile(r'^(\S*)\s+(.+?)\s+\-\s+(.+?)\s+(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('flatpak', 'Flatpak')

    def test_installed(self):
        return self.call('which flatpak 2>/dev/null') != ''

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self.call("flatpak search \"{0}\" --columns=version,description,application,remotes".format(name), self.search_regex, None, True)
        results = []
        for row in table:
            id = row[4] + ':' + row[3]
            results.append(App(self, id, row[1], row[2], row[0], installedids.get(id, '')))
        return results

    def local(self, name):
        installed = self._get_installed()
        results = []
        for app in installed:
            if name == None or app.match(name):
                remoteapp = self.getapp(app.id)
                app.version = remoteapp.version
                results.append(app)
        return results

    def getapp(self, appid):
        remote, id = self._split_id(appid)
        results = self.search(id)
        for result in results:
            if result.id == appid:
                return result
        return None

    def install(self, app):
        remote, id = self._split_id(app.id)
        self.call("flatpak install -y {0} {1}".format(remote, id))

    def remove(self, app):
        remote, id = self._split_id(app.id)
        self.call("flatpak remove -y {0}".format(id))

    def _split_id(self, name):
        i = name.index(':')
        return (name[0:i], name[i + 1:])

    def _get_installed(self):
        table = self.call("flatpak list --columns=version,description,application,origin", self.search_regex, None, True)
        results = []
        for row in table:
            id = row[4] + ':' + row[3]
            results.append(App(self, id, row[1], row[2], None, row[0]))
        return results

    def _get_installed_ids(self):
        installed = self._get_installed()
        installedids = {}
        for installedapp in installed:
            installedids[installedapp.id] = installedapp.installed
        return installedids
