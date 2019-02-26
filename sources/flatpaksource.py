#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class FlatpakSource(AbstractSource):

    ids_regex = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(.+)$')
    description_regex = re.compile(r'^\s*([^\:]+?)\:\s+(.+)$')
    name_description_regex = re.compile(r'^([^\-]+)\s+\-\s+(.+)$')

    def __init__(self):
        super().__init__('flatpak', 'Flatpak')
        self.executor = CommandExecutor()
        self.user = self.executor.getuser()

    def testinstalled(self):
        return self.executor.call('which flatpak 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        pass

    def search(self, name):
        table = self.executor.call("flatpak search \"{0}\" --columns=remotes,application,branch,description".format(name), self.ids_regex, None, True)
        results = []
        for row in table:
            appid = self._make_id(row[0], row[1], row[2])
            app = self.getapp(appid)
            if app is None:
                if len(appid.split('.')) >= 3: # Workaround due to some flatpak apps having invalid IDs
                    raise Exception("Could not find app {0} in results".format(appid))
            else:
                results.append(app)
        return results

    def local(self, name):
        installedids = self._get_installed_ids()
        results = []
        for appid in installedids:
            localapp = installedids[appid]
            if name is None or localapp.match(name):
                app = self.getapp(appid)
                if app is None:
                    if len(appid.split('.')) >= 3: # Workaround due to some flatpak apps having invalid IDs
                        raise Exception("Could not find app {0} in results".format(appid))
                else:
                    results.append(app)
        return results

    def getapp(self, appid):
        remote, id, branch = self._split_id(appid)
        app = FlatpakApp(self, appid, '', '', None, None, False, None, None)

        output = self.executor.call("sudo -u {0} flatpak info {1}".format(self.user, id), None, None, True, [0, 1])
        for line in output.splitlines():
            match = self.name_description_regex.match(line)
            if match:
                app.user = True
                row = match.groups()
                if app.name == '':
                    app.name = row[0]
                if app.desc == '':
                    app.desc = row[1]
            match = self.description_regex.match(line)
            if match:
                row = match.groups()
                if row[0] == 'Version':
                    app.installed = row[1]
                if row[0] == 'Commit':
                    app.local_checksum = row[1]

        output = self.executor.call("flatpak info {0}".format(id), None, None, True, [0, 1])
        for line in output.splitlines():
            match = self.name_description_regex.match(line)
            if match:
                app.user = False
                row = match.groups()
                if app.name == '':
                    app.name = row[0]
                if app.desc == '':
                    app.desc = row[1]
            match = self.description_regex.match(line)
            if match:
                row = match.groups()
                if row[0] == 'Version':
                    app.installed = row[1]
                if row[0] == 'Commit':
                    app.local_checksum = row[1]

        output = self.executor.call("flatpak remote-info {0} {1}//{2}".format(remote, id, branch), None, None, True, [0, 1])
        for line in output.splitlines():
            match = self.name_description_regex.match(line)
            if match:
                row = match.groups()
                if app.name == '':
                    app.name = row[0]
                if app.desc == '':
                    app.desc = row[1]
            match = self.description_regex.match(line)
            if match:
                row = match.groups()
                if row[0] == 'Version':
                    app.version = row[1]
                if row[0] == 'Commit':
                    app.remote_checksum = row[1]
        
        if app.local_checksum is None and app.remote_checksum is None:
            return None
        return app

    def install(self, app):
        remote, id, branch = self._split_id(app.id)
        if app.user:
            self.executor.call("sudo -u {0} flatpak --user install -y {1} {2}".format(self.user, remote, id))
        else:
            self.executor.call("flatpak install -y {0} {1}".format(remote, id))

    def remove(self, app):
        remote, id, branch = self._split_id(app.id)
        if app.user:
            self.executor.call("sudo -u {0} flatpak --user remove -y {1}".format(self.user, id))
        else:
            self.executor.call("flatpak remove -y {0}".format(id))

    def update(self, apps, autoconfirm):
        for app in apps:
            remote, id, branch = self._split_id(app.id)
            if app.user:
                self.executor.call("sudo -u {0} flatpak --user update --assumeyes {1}".format(self.user, id))
            else:
                self.executor.call("flatpak update --assumeyes {0}".format(id))
        return None

    def _make_id(self, remote, id, branch):
        return "{0}:{1}:{2}".format(remote, id, branch)

    def _split_id(self, appid):
        elements = appid.split(':')
        if len(elements) != 3:
            raise Exception("{0} is not a valid Flatpak app ID".format(appid))
        return elements

    def _get_installed_ids(self):
        table = self.executor.call("flatpak list --columns=origin,application,branch,description", self.ids_regex, None, True)
        systemapps = len(table)
        table += self.executor.call("sudo -u {0} flatpak list --columns=origin,application,branch,description".format(self.user), self.ids_regex, None, True)
        results = {}
        for i, row in enumerate(table):
            appid = self._make_id(row[0], row[1], row[2])
            name = row[3]
            desc = ''
            match = self.name_description_regex.match(name)
            if match:
                matchgroups = match.groups()
                name = matchgroups[0]
                desc = matchgroups[1]
            results[appid] = FlatpakApp(self, appid, name, desc, None, None, (i >= systemapps), None, None)
        return results


class FlatpakApp(App):

    def __init__(self, source, id, name, desc, version, installed, user, remote_checksum, local_checksum):
        super().__init__(source, id, name, desc, version, installed, user)
        self.remote_checksum = remote_checksum
        self.local_checksum = local_checksum

    def status(self):
        indicator = 'N'
        if self.local_checksum is not None:
            indicator = 'I'
            if self.remote_checksum != self.local_checksum and self.remote_checksum is not None:
                indicator = 'U'
        return indicator

    def isinstalled(self):
        return (self.local_checksum is not None);
