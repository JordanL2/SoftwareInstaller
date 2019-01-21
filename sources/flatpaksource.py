#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class FlatpakSource(AbstractSource):

    #search_regex = re.compile(r'^(\S*)\s+(.+?)\s+\-\s+(.+?)\s+(\S+)\s+(\S+)\s+(\S+)$')
    ids_regex = re.compile(r'^(\S+)\s+(\S+)$')
    description_regex = re.compile(r'^\s*([^\:]+?)\:\s+(.+)$')
    name_description_regex = re.compile(r'^([^\-]+)\s+\-\s+(.+)$')

    def __init__(self):
        super().__init__('flatpak', 'Flatpak')
        self.executor = CommandExecutor()

    def testinstalled(self):
        return self.executor.call('which flatpak 2>/dev/null') != ''

    def refresh(self):
        pass

    def search(self, name):
        table = self.executor.call("flatpak search \"{0}\" --columns=application,remotes".format(name), self.ids_regex, None, True)
        results = []
        for row in table:
            appid = row[1] + ':' + row[0]
            app = self.getapp(appid)
            if app is None:
                print(appid)
            results.append(app)
        return results

    def local(self, name):
        installedids = self._get_installed_ids()
        results = []
        for id in installedids:
            app = self.getapp(id)
            if app is None:
                print(appid)
            if name is None or app.match(name):
                results.append(app)
        return results

    def getapp(self, appid):
        remote, id = self._split_id(appid)
        app = FlatpakApp(self, appid, '', '', None, None, None, None, None)

        table = self.executor.call("flatpak info {0} | head -n2 | tail -n1".format(id), self.name_description_regex, None, True, [0, 1])
        for row in table:
            app.name = row[0]
            app.desc = row[1]
        table = self.executor.call("flatpak info {0}".format(id), self.description_regex, None, True, [0, 1])
        for row in table:
            if row[0] == 'Version':
                app.installed = row[1]
            if row[0] == 'Commit':
                app.local_checksum = row[1]
            if row[0] == 'Branch':
                app.branch = row[1]

        table = self.executor.call("flatpak remote-info {0} {1} | head -n2 | tail -n1".format(remote, id), self.name_description_regex, None, True, [0, 1])
        for row in table:
            if app.name == '':
                app.name = row[0]
            if app.desc == '':
                app.desc = row[1]
        table = self.executor.call("flatpak remote-info {0} {1}".format(remote, id), self.description_regex, None, True, [0, 1])
        for row in table:
            if row[0] == 'Version':
                app.version = row[1]
            if row[0] == 'Commit':
                app.remote_checksum = row[1]
            if row[0] == 'Branch' and app.branch is None:
                app.branch = row[1]
        
        if app.branch is None:
            return None
        return app

    def install(self, app):
        remote, id = self._split_id(app.id)
        self.executor.call("flatpak install -y {0} {1}".format(remote, id))

    def remove(self, app):
        remote, id = self._split_id(app.id)
        self.executor.call("flatpak remove -y {0}".format(id))

    def update(self, apps, autoconfirm):
        #TODO
        print("Updating:", [a.id for a in apps])
        #for app in apps:
        #    self.executor.call("flatpak update --assumeyes {0}".format(app.id))
        return None

    def _split_id(self, appid):
        if ':' not in appid:
            raise Exception("{0} is not a valid Flatpak app ID".format(appid))
        i = appid.index(':')
        return (appid[0:i], appid[i + 1:])

    def _get_installed_ids(self):
        table = self.executor.call("flatpak list --columns=application,origin", self.ids_regex, None, True)
        results = []
        for row in table:
            results.append(row[1] + ":" + row[0])
        return results


class FlatpakApp(App):

    def __init__(self, source, id, name, desc, version, installed, remote_checksum, local_checksum, branch):
        super().__init__(source, id, name, desc, version, installed)
        self.remote_checksum = remote_checksum
        self.local_checksum = local_checksum
        self.branch = branch

    def status(self):
        indicator = 'N'
        if self.installed is not None:
            indicator = 'I'
            if self.remote_checksum != self.local_checksum:
                indicator = 'U'
        return indicator
