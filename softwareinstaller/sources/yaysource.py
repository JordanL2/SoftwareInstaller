#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class YaySource(AbstractSource):

    search_regex = re.compile(r'^[^\/]+\/(\S+)\s+(\S+)\s+(\S+)\s+[^\,]+,(.*)$')
    description_regex = re.compile(r'^\s*([^\:]+?)\s+\:\s+(.+)$')
    installed_regex = re.compile(r'^(\S+)\s+(\S+)$')

    def __init__(self, service):
        super().__init__(service, 'yay', 'Yay')
        self.executor = CommandExecutor()

        # Some AUR packages report a different latest version to the one that gets installed
        self.check_updated = False

        self.user = self.executor.getuser()

    def testinstalled(self):
        return self.executor.call('which yay 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        self.executor.call("sudo -u {0} yay -Sy".format(self.user))

    def search(self, terms):
        start_time = time.perf_counter()

        installedids = self._get_installed_ids()

        search_string = "sudo -u {0} yay -Ss \"{1}\" | sed -e \"s/    //\" | paste -d, - - | grep \"^aur/\"".format(self.user, terms[0])
        for term in terms[1:]:
            search_string += " | grep -i \"{0}\"".format(term)

        table = self.executor.call(search_string, self.search_regex, None, False, [0, 1])
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[3], row[1], installedids.get(row[0])))

        self.log('performance', "yay search {}".format(time.perf_counter() - start_time))
        return results

    def local(self, terms):
        start_time = time.perf_counter()
        installedids = self._get_installed_ids()
        results = []
        apps = self.getapps(installedids.keys(), installedids)
        for app in apps:
            if terms is None or app.match(terms):
                results.append(app)

        self.log('performance', "yay local {}".format(time.perf_counter() - start_time))
        return results

    def getapp(self, appid):
        return self.getapps([appid])[0]

    def getapps(self, appids, installedids=None):
        start_time = time.perf_counter()
        if installedids is None:
            installedids = self._get_installed_ids()

        apps = []
        table = self.executor.call("sudo -u {0} yay -Si {1}".format(self.user, ' '.join(appids)), self.description_regex, None, True, [0, 1])
        for row in table:
            if row[0] == 'Name':
                apps.append(App(self, row[1], row[1], '', None, installedids.get(row[1])))
            if row[0] == 'Description':
                apps[-1].desc = row[1]
            if row[0] == 'Version':
                apps[-1].version = row[1]

        founds_ids = [a.id for a in apps]
        for appid in appids:
            if appid not in founds_ids:
                app = App(self, appid, appid, '', None, installedids.get(appid))
                version = None
                table = self.executor.call("sudo -u {0} yay -Qi {1}".format(self.user, appid), self.description_regex, None, True, [0, 1])
                for row in table:
                    if row[0] == 'Description':
                        app.desc = row[1]
                apps.append(app)

        self.log('performance', "yay getapps {}".format(time.perf_counter() - start_time))
        return apps

    def install(self, app):
        self.executor.call("sudo -u {0} yay --noconfirm -S {1}".format(self.user, app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def remove(self, app):
        self.executor.call("sudo -u {0} yay --noconfirm -R {1}".format(self.user, app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def update(self, apps, autoconfirm):
        app_list = self._determine_update_order(apps)
        for app in app_list:
            self.executor.call("sudo -u {0} yay -S {1} --noconfirm".format(self.user, app.id), stdout=self.service.output_std, stderr=self.service.output_err)
        return None

    def _get_installed_ids(self):
        table = self.executor.call("sudo -u {0} yay -Qm".format(self.user), self.installed_regex, None, False, [0, 1])
        return dict([(row[0], row[1]) for row in table])

    def _determine_update_order(self, apps):
        newlist = []
        appids = dict([(a.id, a) for a in apps])
        for app in apps:
            self._add_app_to_list(newlist, app, appids)

        return newlist

    def _add_app_to_list(self, newlist, app, appids):
        if app not in newlist:
            deps = self._get_app_deps(app)
            for dep in deps:
                if dep in appids:
                    self._add_app_to_list(newlist, appids[dep], appids)
            newlist.append(app)

    def _get_app_deps(self, app):
        table = self.executor.call("sudo -u {0} yay -Qi {1}".format(self.user, app.id), self.description_regex, None, True, [0, 1])
        for row in table:
            if row[0] == 'Depends On':
                deps = row[1].split()
                for i, dep in enumerate(deps):
                    if '=' in dep:
                        deps[i] = dep[0 : dep.index('=')]
                return deps
        return []
