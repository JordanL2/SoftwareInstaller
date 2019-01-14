#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re

class FlatpakSource(AbstractSource):

    search_regex = re.compile(r'^(.+?)\s+\-\s+(.+)\s+(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('flatpak', 'Flatpak')

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self.call("flatpak search {0}  --columns=description,application,remotes".format(name), self.search_regex, None, True)
        results = []
        for row in table:
            id = row[3] + ':' + row[2]
            results.append(App(self, id, row[0], row[1], id in installedids))
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
        table = self.call("flatpak list --columns=description,application,origin", self.search_regex, None, True)
        return [App(self, row[3] + ':' + row[2], row[0], row[1], False) for row in table]

    def _get_installed_ids(self):
        installed = self._get_installed()
        installedids = set()
        for installedapp in installed:
            installedids.add(installedapp.id)
        return installedids
