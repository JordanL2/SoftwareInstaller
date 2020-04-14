#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re
from xml.etree import ElementTree


class FlatpakSource(AbstractSource):

    ids_regex = re.compile(r'^(\S*\s+)(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$')
    search_regex = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$')
    description_regex = re.compile(r'^\s*([^\:]+?)\:\s+(.+)$')
    name_description_regex = re.compile(r'^([^\-]+)\s+\-\s+(.+)$')
    remote_regex = re.compile(r'^(\S*\s+)(\S+)\s+(\S+)\s+(\S+)\s*(.*)$')

    def __init__(self, service):
        super().__init__(service, 'flatpak', 'Flatpak')
        self.executor = CommandExecutor()
        self.user = self.executor.getuser()
        self.config_options['defaultmode'] = [str, 'system']

    def testinstalled(self):
        return self.executor.call('which flatpak 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        pass

    def search(self, terms):
        start_time = time.perf_counter()

        all_apps = self._get_installed(getall=True)
        results = {}
        for user in False, True:
            if user:
                search_string = "sudo -u {0} flatpak search --user \"{1}\" --columns=remotes,application,branch,description".format(self.user, terms[0])
            else:
                search_string = "flatpak search \"{0}\" --columns=remotes,application,branch,description".format(terms[0])
            for term in terms[1:]:
                search_string += " | grep -i \"{0}\"".format(term)

            table = self.executor.call(search_string, self.search_regex, None, True, [0, 1])
            for row in table:
                appid = self._make_id(row[0], row[1], row[2])
                results[appid] = all_apps[appid]

        self.log('performance', "flatpak search {}".format(time.perf_counter() - start_time))
        return results.values()

    def local(self, terms):
        start_time = time.perf_counter()

        installedids = self._get_installed()
        results = []
        for appid, localapp in installedids.items():
            if terms is None or localapp.match(terms):
                results.append(localapp)

        self.log('performance', "flatpak local {}".format(time.perf_counter() - start_time))
        return results

    def getapp(self, appid):
        start_time = time.perf_counter()
        remote, id, branch = self._split_id(appid)
        app = FlatpakApp(self, appid, '', '', None, None, False, None, None)

        output = self.executor.call("sudo -u {0} flatpak info {1}//{2}".format(self.user, id, branch), None, None, True, [0, 1])
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
        self.log('performance', "flatpak getapp local user {}".format(time.perf_counter() - start_time))
        start_time = time.perf_counter()

        if app.local_checksum is None:
            output = self.executor.call("flatpak info {0}//{1}".format(id, branch), None, None, True, [0, 1])
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
            self.log('performance', "flatpak getapp local system {}".format(time.perf_counter() - start_time))
            start_time = time.perf_counter()

        output = self.executor.call("sudo -u {0} flatpak remote-info {1} {2}//{3}".format(self.user, remote, id, branch), None, None, True, [0, 1])
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
        self.log('performance', "flatpak getapp remote user {}".format(time.perf_counter() - start_time))
        start_time = time.perf_counter()

        if app.remote_checksum is None:
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
            self.log('performance', "flatpak getapp remote system {}".format(time.perf_counter() - start_time))

        if app.local_checksum is None and app.remote_checksum is None:
            return None
        return app

    def install(self, app):
        remote, id, branch = self._split_id(app.id)
        if app.user is None:
            if self.service.config['sources.flatpak.defaultmode'] == 'user':
                app.user = True
            else:
                app.user = False
        if app.user:
            self.executor.call("sudo -u {0} flatpak --user install -y {1} {2}".format(self.user, remote, id), stdout=self.service.output_std, stderr=self.service.output_err)
        else:
            self.executor.call("flatpak install -y {0} {1}".format(remote, id), stdout=self.service.output_std, stderr=self.service.output_err)

    def remove(self, app):
        remote, id, branch = self._split_id(app.id)
        if app.user:
            self.executor.call("sudo -u {0} flatpak --user remove -y {1}".format(self.user, id), stdout=self.service.output_std, stderr=self.service.output_err)
        else:
            self.executor.call("flatpak remove -y {0}".format(id), stdout=self.service.output_std, stderr=self.service.output_err)

    def update(self, apps, autoconfirm):
        for app in apps:
            remote, id, branch = self._split_id(app.id)
            if app.user:
                self.executor.call("sudo -u {0} flatpak --user update --assumeyes {1}".format(self.user, id), stdout=self.service.output_std, stderr=self.service.output_err)
            else:
                self.executor.call("sudo -u {0} flatpak update --assumeyes {1}".format(self.user, id), stdout=self.service.output_std, stderr=self.service.output_err)
        return None

    def _make_id(self, remote, id, branch):
        return "{0}:{1}:{2}".format(remote, id, branch)

    def _split_id(self, appid):
        elements = appid.split(':')
        if len(elements) != 3:
            raise Exception("{0} is not a valid Flatpak app ID".format(appid))
        return elements

    def _get_installed(self, getall=False):
        remote_apps = self._get_remote_info()

        start_time = time.perf_counter()
        table = self.executor.call("flatpak list --columns=version,origin,application,branch,active,name", self.ids_regex, None, True)
        systemapps = len(table)
        table += self.executor.call("sudo -u {0} flatpak list --columns=version,origin,application,branch,active,name".format(self.user), self.ids_regex, None, True)
        results = {}
        for i, row in enumerate(table):
            appid = self._make_id(row[1], row[2], row[3])
            name = row[5]
            results[appid] = FlatpakApp(self, appid, name, '', None, row[0].strip(), (i >= systemapps), None, row[4])
            if appid in remote_apps:
                results[appid].version = remote_apps[appid]['version']
                results[appid].remote_checksum = remote_apps[appid]['remote_checksum']

        if getall:
            for appid, app in remote_apps.items():
                if appid not in results:
                    results[appid] = FlatpakApp(self, appid, app['name'], '', app['version'], None, None, app['remote_checksum'], None)

        self.log('performance', "flatpak _get_installed_ids {}".format(time.perf_counter() - start_time))
        return results

    def _get_remote_info(self):
        start_time = time.perf_counter()
        remote_apps = {}
        remotes_done = set()
        for user in False, True:
            remotes = self._get_remotes(user)
            for remote in remotes:
                if remote not in remotes_done:
                    if user:
                        table = self.executor.call("sudo -u {} flatpak --user remote-ls {} --columns=version,application,branch,commit,name".format(self.user, remote), self.remote_regex, None, True)
                    else:
                        table = self.executor.call("flatpak remote-ls {} --columns=version,application,branch,commit,name".format(remote), self.remote_regex, None, True)
                    for row in table:
                        id = row[1]
                        branch = row[2]
                        appid = self._make_id(remote, id, branch)
                        remote_apps[appid] = {
                            'version': row[0].strip(),
                            'remote_checksum': row[3],
                            'name': row[4]
                        }
                    self.log('performance', "flatpak _get_installed_ids parse appstream {} {}".format(remote, time.perf_counter() - start_time))
                    start_time = time.perf_counter()
                    remotes_done.add(remote)
        return remote_apps

    def _get_remotes(self, user):
        if user:
            return self.executor.call("sudo -u {} flatpak remotes | cut -f1".format(self.user)).splitlines()
        else:
            return self.executor.call("flatpak remotes | cut -f1").splitlines()


class FlatpakApp(App):

    def __init__(self, source, id, name, desc, version, installed, user, remote_checksum, local_checksum):
        super().__init__(source, id, name, desc, version, installed, user)
        self.remote_checksum = remote_checksum
        self.local_checksum = local_checksum

    def status(self):
        indicator = 'N'
        if self.local_checksum is not None:
            indicator = 'I'
            if self.remote_checksum is not None and self.remote_checksum != self.local_checksum and self.remote_checksum is not None:
                indicator = 'U'
        return indicator

    def isinstalled(self):
        return (self.local_checksum is not None);
