#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re
import subprocess

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

    def installapp(self, app):
        #TODO
        pass

    def removeapp(self, app):
        #TODO
        pass

    def _split_id(self, name):
        i = name.index(':')
        return (name[0:i], name[i + 1:])

    def _get_installed(self):
        table = self.call("flatpak list --app --columns=description,application,origin", self.search_regex, None, True)
        results = []
        for row in table:
            results.append(App(self, row[3] + ':' + row[2], row[0], row[1], False))
        return results

    def _get_installed_ids(self):
        installed = self._get_installed()
        installedids = set()
        for installedapp in installed:
            installedids.add(installedapp.id)
        return installedids
