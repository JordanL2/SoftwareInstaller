#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re
from xml.etree import ElementTree


class FlatpakSource(AbstractSource):

    ids_regex = re.compile(r'^([^\t]*)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t*([^\t]*)$')
    search_regex = re.compile(r'^([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t*([^\t]*)$')
    description_regex = re.compile(r'^\s*([^\:]+?)\:\s+(.+)$')
    name_description_regex = re.compile(r'^([^\-]+)\s+\-\s+(.+)$')
    remote_regex = re.compile(r'^([^\t]*)\t+([^\t]+)\t+([^\t]+)\t+([^\t]+)\t*([^\t]*)$')

    def __init__(self, service):
        super().__init__(service, 'flatpak', 'Flatpak')
        self.executor = CommandExecutor()
        self.user = self.executor.getuser()

    def _cmd(self, cmd, user):
        if user:
            return "sudo -u {0} sh -c \"flatpak --user {1}\"".format(self.user, cmd.replace('"', '\\"'))
        else:
            return "flatpak --system {0}".format(cmd)

    def testinstalled(self):
        return self.executor.call('which flatpak 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        pass

    def search(self, terms):
        start_time = time.perf_counter()

        all_apps = self._get_installed(getall=True)
        results = {}
        for user in False, True:
            search_string = self._cmd("search \"{0}\" --columns=remotes,application,branch,description".format(terms[0]), user)
            for term in terms[1:]:
                search_string += " | grep -i \"{0}\"".format(term)

            table = self.executor.call(search_string, self.search_regex, None, True, [0, 1])
            for row in table:
                appid = self._make_id(row[0], row[1], row[2], user)
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
        remote, id, branch, user = self._split_id(appid)
        app = FlatpakApp(self, appid, '', '', None, None, None, None)

        if user:
            output = self.executor.call(self._cmd("info {0}//{1}".format(id, branch), True), None, None, True, [0, 1])
            matching_remote = False
            name = ''
            desc = ''
            installed = None
            local_checksum = None
            for line in output.splitlines():
                match = self.name_description_regex.match(line)
                if match:
                    row = match.groups()
                    if name == '':
                        name = row[0]
                    if desc == '':
                        desc = row[1]
                match = self.description_regex.match(line)
                if match:
                    row = match.groups()
                    if row[0] == 'Version':
                        installed = row[1]
                    if row[0] == 'Commit':
                        local_checksum = row[1]
                    if row[0] == 'Origin' and row[1] == remote:
                        matching_remote = True
            if matching_remote:
                app.name = name
                app.desc = desc
                app.installed = installed
                app.local_checksum = local_checksum
            self.log('performance', "flatpak getapp local user {}".format(time.perf_counter() - start_time))
            start_time = time.perf_counter()

            output = self.executor.call(self._cmd("remote-info {0} {1}//{2}".format(remote, id, branch), True), None, None, True, [0, 1])
            for line in output.splitlines():
                if app.version is None:
                    app.version = ''
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

        else:
            output = self.executor.call(self._cmd("info {0}//{1}".format(id, branch), False), None, None, True, [0, 1])
            matching_remote = False
            name = ''
            desc = ''
            installed = None
            local_checksum = None
            for line in output.splitlines():
                match = self.name_description_regex.match(line)
                if match:
                    row = match.groups()
                    if name == '':
                        name = row[0]
                    if desc == '':
                        desc = row[1]
                match = self.description_regex.match(line)
                if match:
                    row = match.groups()
                    if row[0] == 'Version':
                        installed = row[1]
                    if row[0] == 'Commit':
                        local_checksum = row[1]
                    if row[0] == 'Origin' and row[1] == remote:
                        matching_remote = True
            if matching_remote:
                app.name = name
                app.desc = desc
                app.installed = installed
                app.local_checksum = local_checksum
            self.log('performance', "flatpak getapp local system {}".format(time.perf_counter() - start_time))
            start_time = time.perf_counter()

            output = self.executor.call(self._cmd("remote-info {0} {1}//{2}".format(remote, id, branch), False), None, None, True, [0, 1])
            for line in output.splitlines():
                if app.version is None:
                    app.version = ''
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
        remote, id, branch, user = self._split_id(app.id)
        self.executor.call(self._cmd("install -y {0} {1}".format(remote, id), user), stdout=self.service.output_std, stderr=self.service.output_err)

    def remove(self, app):
        remote, id, branch, user = self._split_id(app.id)
        self.executor.call(self._cmd("remove -y {0}".format(id), user), stdout=self.service.output_std, stderr=self.service.output_err)

    def update(self, apps, autoconfirm):
        for app in apps:
            remote, id, branch, user = self._split_id(app.id)
            self.executor.call(self._cmd("update --assumeyes {0}".format(id), user), stdout=self.service.output_std, stderr=self.service.output_err)
        return None

    def _make_id(self, remote, id, branch, user):
        # Sometimes flatpak search returns ids with the '.desktop' missing
        if len([l for l in id if l == '.']) < 2:
            id += '.desktop'
        return "{1}{0}{2}{0}{3}{0}{4}".format(self.service.config['apps.ref.delimiter'], remote, id, branch, ('user' if user else 'system'))

    def _split_id(self, appid):
        elements = appid.split(self.service.config['apps.ref.delimiter'])
        if len(elements) != 4:
            raise Exception("{0} is not a valid Flatpak app ID".format(appid))
        elements[3] = (elements[3] == 'user')
        return elements

    def _get_installed(self, getall=False):
        remote_apps = self._get_remote_info()

        start_time = time.perf_counter()
        table = self.executor.call(self._cmd("list --columns=version,origin,application,branch,active,name", False), self.ids_regex)
        systemapps = len(table)
        table += self.executor.call(self._cmd("list --columns=version,origin,application,branch,active,name", True), self.ids_regex)
        results = {}
        for i, row in enumerate(table):
            appid = self._make_id(row[1], row[2], row[3], (i >= systemapps))
            name = row[5]
            results[appid] = FlatpakApp(self, appid, name, '', None, row[0].strip(), None, row[4])
            if appid in remote_apps:
                results[appid].version = remote_apps[appid]['version']
                results[appid].remote_checksum = remote_apps[appid]['remote_checksum']

        if getall:
            for appid, app in remote_apps.items():
                if appid not in results:
                    results[appid] = FlatpakApp(self, appid, app['name'], '', app['version'], None, app['remote_checksum'], None)

        self.log('performance', "flatpak _get_installed_ids {}".format(time.perf_counter() - start_time))
        return results

    def _get_remote_info(self):
        start_time = time.perf_counter()
        remote_apps = {}
        for user in False, True:
            remotes = self._get_remotes(user)
            for remote in remotes:
                table = self.executor.call(self._cmd("remote-ls {} --columns=version,application,branch,commit,name".format(remote), user), self.remote_regex)
                for row in table:
                    id = row[1]
                    branch = row[2]
                    appid = self._make_id(remote, id, branch, user)
                    remote_apps[appid] = {
                        'version': row[0].strip(),
                        'remote_checksum': row[3],
                        'name': row[4]
                    }
                self.log('performance', "flatpak _get_installed_ids parse appstream {} {}".format(remote, time.perf_counter() - start_time))
                start_time = time.perf_counter()
        return remote_apps

    def _get_remotes(self, user):
        return self.executor.call(self._cmd("remotes | cut -f1", user)).splitlines()


class FlatpakApp(App):

    def __init__(self, source, id, name, desc, version, installed, remote_checksum, local_checksum):
        super().__init__(source, id, name, desc, version, installed)
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
