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

    def testinstalled(self):
        return self.executor.call('which yay 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        self.executor.call("yay -Sy")

    def search(self, terms):
        start_time = time.perf_counter()

        installedids = self._get_installed_ids()

        search_string = "yay -Ss \"{0}\" | sed -e \"s/    //\" | paste -d, - - | grep \"^aur/\"".format(terms[0])
        for term in terms[1:]:
            search_string += " | grep -i \"{0}\"".format(term)

        table = self.executor.call(search_string, self.search_regex, None, False, [0, 1])
        results = []
        for row in table:
            results.append(App(self, row[0], row[0], row[3], row[1], installedids.get(row[0]), False))

        self.log_performance("yay search {}".format(time.perf_counter() - start_time))
        return results

    def local(self, terms):
        start_time = time.perf_counter()
        installedids = self._get_installed_ids()
        results = []
        apps = self.getapps(installedids.keys(), installedids)
        for app in apps:
            if terms is None or app.match(terms):
                results.append(app)

        self.log_performance("yay local {}".format(time.perf_counter() - start_time))
        return results

    def getapp(self, appid):
        return self.getapps([appid])[0]

    def getapps(self, appids, installedids=None):
        start_time = time.perf_counter()
        if installedids is None:
            installedids = self._get_installed_ids()

        apps = []
        table = self.executor.call("yay -Si {0}".format(' '.join(appids)), self.description_regex, None, True, [0, 1])
        for row in table:
            if row[0] == 'Name':
                apps.append(App(self, row[1], row[1], '', None, installedids.get(row[1]), False))
            if row[0] == 'Description':
                apps[-1].desc = row[1]
            if row[0] == 'Version':
                apps[-1].version = row[1]

        founds_ids = [a.id for a in apps]
        for appid in appids:
            if appid not in founds_ids:
                app = App(self, appid, appid, '', None, installedids.get(appid), False)
                version = None
                table = self.executor.call("yay -Qi {0}".format(appid), self.description_regex, None, True, [0, 1])
                for row in table:
                    if row[0] == 'Description':
                        app.desc = row[1]
                apps.append(app)

        self.log_performance("yay getapps {}".format(time.perf_counter() - start_time))
        return apps

    def install(self, app):
        user = self.executor.getuser()
        self.executor.call("sudo -u {0} yay --noconfirm -S {1}".format(user, app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def remove(self, app):
        self.executor.call("yay --noconfirm -R {0}".format(app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def update(self, apps, autoconfirm):
        user = self.executor.getuser()
        for app in apps:
            self.executor.call("sudo -u {0} yay -S {1} --noconfirm".format(user, app.id), stdout=self.service.output_std, stderr=self.service.output_err)
        return None

    def _get_installed_ids(self):
        table = self.executor.call("yay -Qm", self.installed_regex, None, False, [0, 1])
        return dict([(row[0], row[1]) for row in table])
