#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService
from softwareinstaller.app import App

import csv
import sys


class SoftwareInstallerCLI:

    def __init__(self):
        self.service = SoftwareService()
        self.load_config()
        self.service.load_sources()
        
        self.service.output_std = sys.stdout
        self.service.output_err = sys.stderr
        self.service.output_log['performance'] = sys.stderr

        self.valid_flags = set(['--status', '--source', '--csv', '--columns', '-y', '--force', '--DEBUG-performance'])

    def load_config(self):
        config_dir = "/home/{}/.config".format(self.service.executor.getuser())
        filename = "{}/softwareinstaller/config".format(config_dir)

        lines = []
        try:
            fh = open(filename, 'r')
            lines = fh.readlines()
        except:
            pass

        for line in lines:
            line = line.rstrip()
            try:
                split_index = line.index('=')
                key = line[0: split_index]
                value = line[split_index + 1:]
                if key not in self.service.config_options:
                    raise Exception("No such option: '{}'".format(key))
                val_type = self.service.config_options[key][0]
                if val_type == str:
                	self.service.config[key] = value
                elif val_type == bool:
                    if value == 'true':
                        value = True
                    elif value == 'false':
                        value = False
                    else:
                        raise Exception("Invalid boolean: '{}'".format(value))
                    self.service.config[key] = value
                elif val_type == list:
                    self.service.config[key].append(value)
            except Exception as e:
                print("{}\nInvalid line: {}".format(line, e))

    def do_command(self, cmd, args):
        flags_unparsed = [a for a in args if a.startswith('-')]
        args = [a for a in args if not a.startswith('-')]
        flags = {}
        for flag in flags_unparsed:
            key = flag
            value = True
            if '=' in flag:
                key = flag[0:flag.index('=')]
                value = flag[flag.index('=') + 1:]
            if key not in self.valid_flags:
                raise Exception("Invalid flag: {0}".format(key))
            flags[key] = value

        if '--DEBUG-performance' in flags:
        	self.service.debug['performance'] = True

        if cmd == 'search':
            self.search(args, flags)
        elif cmd == 'local':
            self.local(args, flags)
        elif cmd == 'info':
            self.info(args, flags)
        elif cmd == 'install':
            self.install(args, flags)
        elif cmd == 'remove':
            self.remove(args, flags)
        elif cmd == 'update':
            self.update(args, flags)
        elif cmd == 'help' or cmd == '--help':
            self.help()
        else:
            print("Unrecognised command '{0}'".format(cmd))
            print()
            self.help()

    def help(self):
        print("search <TERM>... [--csv] [--status=N,I,U] [--source=<SOURCE>[,<SOURCE>...]] [--columns=<COLUMN>[,<COLUMN>...]]")
        print("local [<TERM>...] [--csv] [--status=N,I,U] [--source=<SOURCE>[,<SOURCE>...]] [--columns=<COLUMN>[,<COLUMN>...]]")
        print("info <REF>")
        print("install <REF>")
        print("remove <REF>")
        print("update [<REF>...] [-y] [--force")

    def search(self, args, flags):
        filters = self._get_status_flag(flags)
        sources = None
        if '--source' in flags:
            sources = [self.service.getsource(s) for s in flags['--source'].split(',')]
        results = self.service.search(args, filters, sources)
        columns = None
        if '--columns' in flags:
            columns = flags['--columns'].split(',')
        self._outputresults(results, flags, columns)

    def local(self, args, flags):
        filters = self._get_status_flag(flags)
        sources = None
        if '--source' in flags:
            sources = [self.service.getsource(s) for s in flags['--source'].split(',')]
        results = self.service.local(args, filters, sources)
        columns = None
        if '--columns' in flags:
            columns = flags['--columns'].split(',')
        self._outputresults(results, flags, columns)

    def info(self, args, flags):
        superid = args.pop(0)
        app = self.service.getapp(superid)
        print('     Name:', app.name)
        print('     Desc:', app.desc)
        print('  Version:', (app.version if app.version is not None else '[Not Found]'))
        if app.installed is not None:
            print('Installed:', app.installed)
        status = {'N': 'Not installed', 'I': 'Installed, up to date', 'U': 'Installed, update available'}[app.status()]
        print('   Status:', status)

    def install(self, args, flags):
        superid = args.pop(0)
        self.service.install(superid)

    def remove(self, args, flags):
        superid = args.pop(0)
        self.service.remove(superid)

    def update(self, args, flags):
        autoconfirm = '-y' in flags
        forcerun = '--force' in flags
        apps = None
        specific = False
        if len(args) > 0:
            specific = True
            applist = [self.service.getapp(i) for i in args]
            apps = {}
            for app in applist:
                if app.source.id not in apps:
                    apps[app.source.id] = []
                apps[app.source.id].append(app)
            for sourceid in apps.keys():
                for app in apps[sourceid]:
                    if app.status() != 'U':
                        if app.status() == 'N':
                            raise Exception("App {0} requested to be updated, but app is not installed".format(app.id))
                        raise Exception("App {0} requested to be updated, but no update available".format(app.id))
        else:
            sources = None
            if '--source' in flags:
                sources = [self.service.getsource(s) for s in flags['--source'].split(',')]
            apps = self.service.local(None, ['U'], sources)
        runtimes = 0
        while (forcerun and runtimes == 0) or (apps is not None and len(apps) > 0):
            if not autoconfirm and not specific and not forcerun:
                self._outputresults(apps, flags, ['SOURCE', 'REF', 'NAME', 'AVAILABLE', 'INSTALLED'])
                text = input("CONFIRM? [y/N]: ")
                if text.lower() != 'y':
                    sys.exit()
            apps = self.service.update(apps, autoconfirm)
            if apps is not None and len(apps) > 0:
                print("WARNING: Some sources cannot only update specific apps, so the list of apps that will be updated has changed.")
            runtimes += 1

    def _outputresults(self, results, flags, header=None):
        table = []
        if header is None:
            header = ['STATUS', 'SOURCE', 'REF', 'NAME', 'AVAILABLE', 'INSTALLED']
        columns = len(header)
        maxwidth = [len(header[i]) for i in range(0, columns)]
        as_csv = '--csv' in flags
        noheader = '--noheader' in flags
        for sourceid in results.keys():
            for result in sorted(results[sourceid], key=lambda x: x.name.lower()):
                indicator = result.status()
                if not as_csv:
                    if indicator == 'N':
                        indicator = '   '
                    else:
                        indicator = "[{0}]".format(indicator)
                row = {
                    'STATUS': indicator,
                    'SOURCE': result.source.name,
                    'REF': self.service.make_superid(sourceid, result.id),
                    'NAME': result.name,
                    'AVAILABLE': (result.version if result.version is not None else '[Not Found]'),
                    'INSTALLED': (result.installed if result.installed is not None else ''),
                }
                if not as_csv:
                    for i in range(0, columns):
                        if len(row[header[i]]) > maxwidth[i]:
                            maxwidth[i] = len(row[header[i]])
                table.append(row)
        if as_csv:
            csvwriter = csv.writer(sys.stdout)
            if not noheader:
                csvwriter.writerow(header)
            csvwriter.writerows(table)
        else:
            if not noheader and len(table) > 0:
                print(str.join(' ', [format(header[i], "<{0}".format(maxwidth[i])) for i in range(0, columns)]))
            for row in table:
                print(str.join(' ', [format(row[header[i]], "<{0}".format(maxwidth[i])) for i in range(0, columns)]))

    def _get_status_flag(self, flags):
        if '--status' in flags:
            filters = flags['--status'].split(',')
            for filter in filters:
                if filter not in App.statuses:
                    raise Exception("Unrecognised filter: {0}".format(filter))
            return filters
        return None


def main():
    cli = SoftwareInstallerCLI()
    scriptpath = sys.argv.pop(0)
    if len(sys.argv) == 0:
        cli.help()
    else:
        cmd = sys.argv.pop(0)
        args = sys.argv.copy()
        cli.do_command(cmd, args)

if __name__ == '__main__':
    main()
