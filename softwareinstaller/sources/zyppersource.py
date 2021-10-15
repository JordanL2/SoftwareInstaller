#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class ZypperSource(AbstractSource):
    
    installed_regex = re.compile(r'^(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.+)$')
    info_name = re.compile(r'Information for package (\S+):')
    info_version = re.compile(r'Version\s+:\s+(\S+)')
    info_installed_uptodate = re.compile(r'Status\s*:\s*up\-to\-date\s*')
    info_installed_outofdate = re.compile(r'Status\s*:\s*out\-of\-date\s+\(version (\S+) installed\)\s*')
    info_desc = re.compile(r'Description\s*:\s*')

    def __init__(self, service):
        super().__init__(service, 'zypper', 'Zypper')
        self.executor = CommandExecutor()
        self.native_only = True #TODO - only set this when an AUR source is in use

    def testinstalled(self):
        return self.executor.call('which zypper 2>/dev/null', None, None, None, [0, 1]) != ''

    def refresh(self):
        self.executor.call("zypper refresh")

    def search(self, terms):
        start_time = time.perf_counter()



        self.log('performance', "zypper search {}".format(time.perf_counter() - start_time))
        return results

    def local(self, terms):
        start_time = time.perf_counter()

        results = []
        installedids = self._get_installed_ids()
        apps = self.getapps(installedids.keys())
        for app in apps:
            if app is not None and (terms is None or app.match(terms)):
                results.append(app)

        self.log('performance', "zypper local {}".format(time.perf_counter() - start_time))
        return results

    def getapp(self, appid):
        start_time = time.perf_counter()
        
        self.log('performance', "zypper getapp {}".format(time.perf_counter() - start_time))
        return self.getapps([appid])[0]

    def getapps(self, appids):
        start_time = time.perf_counter()
        
        apps = []

        appid = None
        desc = None
        available_version = None
        installed_version = None
        
        found_desc = False
        out = self.executor.call("zypper info {0}".format(' '.join(appids)))
        for line in out.split("\n"):
            name_match = self.info_name.match(line)
            if name_match:
                if appid in appids:
                    apps.append(App(self, appid, appid, desc, available_version, installed_version))
                    
                appid = name_match.group(1)
                desc = None
                available_version = None
                installed_version = None
                found_desc = False
                continue

            if found_desc:
                desc += line.strip()
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
        
        apps.append(App(self, appid, appid, desc, available_version, installed_version))
        
        self.log('performance', "zypper getapps {}".format(time.perf_counter() - start_time))
        return apps

    def install(self, app):
        self.executor.call("zypper install -y {0}".format(app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def remove(self, app):
        self.executor.call("zypper remove -yu {0}".format(app.id), stdout=self.service.output_std, stderr=self.service.output_err)

    def update(self, apps, autoconfirm):
        #TODO if the list of packages to be updated has changed, return the new list of packages
        self.executor.call("zypper update -y", stdout=self.service.output_std, stderr=self.service.output_err)
        return None

    def _get_installed_ids(self):
        cmd = "zypper search --installed-only --details"
        table = self.executor.call(cmd, self.installed_regex, None, True)
        return dict([(row[1], row[3]) for row in table])
