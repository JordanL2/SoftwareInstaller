#!/usr/bin/python3

from softwareinstaller.abstractsource import *
from softwareinstaller.commandexecutor import CommandExecutor

import re


class ZypperSource(AbstractSource):
    
    installed_regex = re.compile(r'^(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(.+)$')
    info_version = re.compile(r'Version\s+:\s+(\S+)')
    info_installed_uptodate = re.compile(r'Status\s*:\s*up\-to\-date\s*')
    info_installed_outofdate = re.compile(r'Status\s*:\s*out\-of\-date\s+\(version (\S+) installed\)\s*')
    info_desc = re.compile(r'Description\s*:\s*')
    local_name = re.compile(r'\s*name:\s*(\S+)\s*')
    local_desc = re.compile(r'\s*description:\s*')
    local_packager = re.compile(r'\s*packager:\s*(.*)')
    local_installed = re.compile(r'\s*evr:\s*(\S+)')
    local_arch = re.compile(r'\s*arch:\s*(\S+)\s*')

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
        
        appdatas = {}
        
        # Get installed versions for each installed package
        appid = None
        arch = None
        installed_version = None
        #desc = None
        #found_desc = False
        
        cmd = "zypper search --installed-only --verbose"
        out = self.executor.call(cmd)
        for line in out.split("\n"):
            name_match = self.local_name.match(line)
            if name_match:
                if appid is not None:
                    appdatas["{}|{}".format(appid, arch)] = {
                        'appid': appid,
                        'arch': arch,
                        'installed_version': installed_version,
                        'available_version': installed_version,
                        'desc': '',
                    }
                desc = None
                installed_version = None
                appid = name_match.group(1)
                continue
            installed_match = self.local_installed.match(line)
            if installed_match:
                installed_version = installed_match.group(1)
                continue
            arch_match = self.local_arch.match(line)
            if arch_match:
                arch = arch_match.group(1)
                continue
        if appid is not None:
            appdatas["{}|{}".format(appid, arch)] = {
                'appid': appid,
                'arch': arch,
                'installed_version': installed_version,
                'available_version': installed_version,
                'desc': '',
            }

        notinstalledids = self._get_not_installed_ids()
        
        for appdataid, appdata in appdatas.items():
            available_version = appdata['available_version']
            if appdataid in notinstalledids:
                available_version = notinstalledids[appdataid]
            app = App(self, appdata['appid'], appdata['appid'], appdata['desc'], available_version, appdata['installed_version'])
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
        
        self.log('performance', "zypper getapp {}".format(time.perf_counter() - start_time))
        return App(self, appid, appid, desc, available_version, installed_version)

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

    def _get_not_installed_ids(self):
        cmd = "zypper search --not-installed-only --details"
        table = self.executor.call(cmd, self.installed_regex, None, True)
        return dict([("{}|{}".format(row[1], row[4]), row[3]) for row in table])
