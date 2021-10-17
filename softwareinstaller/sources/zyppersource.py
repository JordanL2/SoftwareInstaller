#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class ZypperSource(AbstractSource):
    
    info_version = re.compile(r'Version\s+:\s+(\S+)')
    info_installed_uptodate = re.compile(r'Status\s*:\s*up\-to\-date\s*')
    info_installed_outofdate = re.compile(r'Status\s*:\s*out\-of\-date\s+\(version (\S+) installed\)\s*')
    info_desc = re.compile(r'Description\s*:\s*')
    search_regex = re.compile(r'^(\S*)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.+)$')
    repos_regex = re.compile(r'(\d+)\s+\|\s+([^|]+?)\s+\|\s+([^|]+?)\s+\|\s+([^|]+?)\s+\|\s+([^|]+?)\s+\|\s+([^|]+?)\s+\|\s+(\d+)')

    def __init__(self, service):
        super().__init__(service, 'zypper', 'Zypper')
        self.executor = CommandExecutor()
        self._init_arch()
        self._init_repos()

    def testinstalled(self):
        return self.executor.call('which zypper 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        self.executor.call("zypper refresh")

    def search(self, terms):
        start_time = time.perf_counter()

        installed, allapps = self._get()
        
        results = []
        for appdataid, appdata in allapps.items():
            installed_version = None
            if appdataid in installed:
                installed_version = installed[appdataid]['version']
            app = App(self, appdata['appid'], appdata['appid'], '', appdata['version'], installed_version)
            if app is not None and (terms is None or app.match(terms)):
                results.append(app)

        self.log('performance', "zypper search {}".format(time.perf_counter() - start_time))
        return results

    def local(self, terms):
        start_time = time.perf_counter()
        
        installed, allapps = self._get()
        
        results = []
        for appdataid, appdata in installed.items():
            available_version = appdata['version']
            if appdataid in allapps:
                available_version = allapps[appdataid]['version']
            app = App(self, appdata['appid'], appdata['appid'], '', available_version, appdata['version'])
            if app is not None and (terms is None or app.match(terms)):
                results.append(app)

        self.log('performance', "zypper local {}".format(time.perf_counter() - start_time))
        return results

    def getapp(self, appid):
        start_time = time.perf_counter()

        desc = None
        available_version = None
        installed_version = None
        found_desc = False
        
        out = self.executor.call("zypper info {0}".format(appid))
        for line in out.split("\n"):
            if found_desc:
                desc += ' ' + line.strip()
                continue
            version_match = self.info_version.match(line)
            if version_match:
                available_version = version_match.group(1)
                continue
            installed_uptodate_match = self.info_installed_uptodate.match(line)
            if installed_uptodate_match:
                installed_version = available_version
                continue
            installed_outofdate_match = self.info_installed_outofdate.match(line)
            if installed_outofdate_match:
                installed_version = installed_outofdate_match.group(1)
                continue
            desc_match = self.info_desc.match(line)
            if desc_match:
                found_desc = True
                desc = ''
        
        self.log('performance', "zypper getapp {}".format(time.perf_counter() - start_time))
        return App(self, appid, appid, desc.strip(), available_version, installed_version)

    def install(self, app):
        self.executor.call("zypper install -y {0}".format(app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def remove(self, app):
        self.executor.call("zypper remove -yu {0}".format(app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def update(self, apps, autoconfirm):
        #TODO if the list of packages to be updated has changed, return the new list of packages
        self.executor.call("zypper update -y", stdout=self.service.output_std, stderr=self.service.output_err)
        return None

    def _get(self):
        installed = {}
        allapps = {}
        
        appid = None
        arch = None
        version = None
        is_installed = False
        
        start_time = time.perf_counter()
        cmd = r'zypper search --details | tail -n+6'
        table = self.executor.call(cmd, self.search_regex)
        self.log('performance', "zypper _get cmd {}".format(time.perf_counter() - start_time))
        
        start_time = time.perf_counter()
        for row in table:
            is_installed = row[0] in ['i', 'i+']
            appid = row[1]
            version = row[3]
            arch = row[4]
            repo = row[5]
            priority = self.repos[repo]
            appdataid = "{}|{}".format(appid, arch)
            if arch in self.arch:
                result = {
                    'appid': appid,
                    'arch': arch,
                    'version': version,
                    'priority': priority,
                }
                if is_installed:
                    installed[appdataid] = result
                if appdataid not in allapps:
                    allapps[appdataid] = result
                elif priority < allapps[appdataid]['priority']:
                    allapps[appdataid]['version'] = version
                    allapps[appdataid]['priority'] = priority
            
        self.log('performance', "zypper _get parsing {}".format(time.perf_counter() - start_time))

        return installed, allapps

    def _init_repos(self):
        cmd = r'zypper repos --priority'
        table = self.executor.call(cmd, self.repos_regex, None, True)
        self.repos = { '(System Packages)': 100 }
        for row in table:
            self.repos[row[2]] = int(row[6])

    def _init_arch(self):
        cmd = r'uname -i'
        out = self.executor.call(cmd)
        arch = out.strip()
        self.arch = ['noarch', arch]
