#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re


class FlatpakSource(AbstractSource):

    search_regex = re.compile(r'^(\S*)\s+(.+?)\s+\-\s+(.+?)\s+(\S+)\s+(\S+)$')

    def __init__(self):
        super().__init__('flatpak', 'Flatpak')

    def testinstalled(self):
        return self._call('which flatpak 2>/dev/null', None, None, True, None) != ''

    def search(self, name):
        installedids = self._get_installed_ids()

        table = self._call("flatpak search \"{0}\" --columns=version,description,application,remotes".format(name), self.search_regex, None, True)
        results = []
        for row in table:
            id = row[4] + ':' + row[3]
            version = row[0]
            if version == '':
                version = '[None]'
            results.append(App(self, id, row[1], row[2], version, installedids.get(id, '')))
        return results

    def local(self, name):
        installed = self._get_installed()
        results = []
        for app in installed:
            if name == None or app.match(name):
                remoteapp = self.getapp(app.id, installed)
                app.version = remoteapp.version
                results.append(app)
        return results

    def getapp(self, appid, installed=None):
        remote, id = self._split_id(appid)
        results = self.search(id)
        for result in results:
            if result.id == appid:
                return result
        if installed == None:
            installed = self._get_installed()
        for app in installed:
            if app.id == appid:
                return app
        return None

    def install(self, app):
        remote, id = self._split_id(app.id)
        self._call("flatpak install -y {0} {1}".format(remote, id))

    def remove(self, app):
        remote, id = self._split_id(app.id)
        self._call("flatpak remove -y {0}".format(id))

    def update(self, apps, autoconfirm):
        #TODO
        print("Updating:", [a.id for a in apps])
        return None

    def _split_id(self, appid):
        if ':' not in appid:
            raise Exception("{0} is not a valid Flatpak app ID".format(appid))
        i = appid.index(':')
        return (appid[0:i], appid[i + 1:])

    def _get_installed(self):
        table = self._call("flatpak list --columns=version,description,application,origin", self.search_regex, None, True)
        results = []
        for row in table:
            id = row[4] + ':' + row[3]
            version = row[0]
            if version == '':
                version = '[None]'
            results.append(App(self, id, row[1], row[2], '[Not Found]', version))
        return results

    def _get_installed_ids(self):
        installed = self._get_installed()
        installedids = {}
        for installedapp in installed:
            installedids[installedapp.id] = installedapp.installed
        return installedids
