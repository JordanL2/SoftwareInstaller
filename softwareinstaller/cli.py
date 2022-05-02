#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService
from softwareinstaller.app import App

import argparse
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

        self.default_columns = ['STATUS', 'SOURCE', 'REF', 'NAME', 'AVAILABLE', 'INSTALLED']
        self.available_columns = ['STATUS', 'SOURCE', 'REF', 'NAME', 'AVAILABLE', 'INSTALLED']

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

    def main(self):
        parser = argparse.ArgumentParser(prog='si')
        subparsers = parser.add_subparsers(title='subcommands', metavar='action', help='action to perform')

        search_parser = subparsers.add_parser('search', help='search remote sources for packages')
        search_parser.add_argument('term', metavar='TERM', nargs='+', help='terms to search for')
        search_parser.add_argument('--source', nargs='*', choices=sorted([s.id for s in self.service.sources]), help='sources to search')
        search_parser.add_argument('--status', nargs='*', choices=['N', 'I', 'U'], help='filter results on installation status: [N]ot installed, [I]nstalled, [U]pdate available')
        search_parser.add_argument('--column', nargs='*', choices=self.available_columns, help='choose the columns in results table')
        search_parser.add_argument('--csv', action='store_true', help='output table in CSV format')
        search_parser.add_argument('--noheader', action='store_true', help='suppress outputting the header row')
        search_parser.set_defaults(func=self.search)

        local_parser = subparsers.add_parser('local', help='search local sources for packages')
        local_parser.add_argument('term', metavar='TERM', nargs='*', help='terms to search for')
        local_parser.add_argument('--source', nargs='*', choices=sorted([s.id for s in self.service.sources]), help='sources to search')
        local_parser.add_argument('--status', nargs='*', choices=['N', 'I', 'U'], help='filter results on installation status: [N]ot installed, [I]nstalled, [U]pdate available')
        local_parser.add_argument('--column', nargs='*', choices=self.available_columns, help='choose the columns in results table')
        local_parser.add_argument('--csv', action='store_true', help='output table in CSV format')
        local_parser.add_argument('--noheader', action='store_true', help='suppress outputting the header row')
        local_parser.set_defaults(func=self.local)

        info_parser = subparsers.add_parser('info', help='show information about a specific package')
        info_parser.add_argument('ref', metavar='REF', type=str, help='package reference')
        info_parser.set_defaults(func=self.info)

        install_parser = subparsers.add_parser('install', help='install a package')
        install_parser.add_argument('ref', metavar='REF', nargs='+', help='package reference')
        install_parser.set_defaults(func=self.install)

        remove_parser = subparsers.add_parser('remove', help='remove a package')
        remove_parser.add_argument('ref', metavar='REF', nargs='+', help='package reference')
        remove_parser.set_defaults(func=self.remove)

        update_parser = subparsers.add_parser('update', help='update packages')
        update_parser.add_argument('ref', metavar='REF', nargs='*', help='package reference')
        update_parser.add_argument('--source', nargs='*', choices=sorted([s.id for s in self.service.sources]), help='sources to update')
        update_parser.add_argument('--noconfirm', action='store_true', help='update without asking for confirmation')
        update_parser.add_argument('--force', action='store_true', help='run pre/post tasks even if there are no updates available')
        update_parser.set_defaults(func=self.update)

        args = parser.parse_args()
        if not hasattr(args, 'func'):
            parser.print_help()
        else:
            args.func(args)

    def search(self, args):
        sources = None
        if args.source is not None:
            sources = [self.service.getsource(s) for s in args.source]
        results = self.service.search(args.term, args.status, sources)
        self._outputresults(results, args)

    def local(self, args):
        sources = None
        if args.source is not None:
            sources = [self.service.getsource(s) for s in args.source]
        results = self.service.local(args.term, args.status, sources)
        self._outputresults(results, args)

    def info(self, args):
        app = self.service.getapp(args.ref)
        print('     Name:', app.name)
        print('     Desc:', app.desc)
        print('  Version:', (app.version if app.version is not None else '[Not Found]'))
        if app.installed is not None:
            print('Installed:', app.installed)
        status = {'N': 'Not installed', 'I': 'Installed, up to date', 'U': 'Installed, update available'}[app.status()]
        print('   Status:', status)

    def install(self, args):
        for ref in args.ref:
            self.service.install(ref)

    def remove(self, args):
        for ref in args.ref:
            self.service.remove(ref)

    def update(self, args):
        noconfirm = args.noconfirm
        forcerun = args.force
        apps = None
        specific = False
        if args.ref is not None and len(args.ref) > 0:
            specific = True
            applist = [self.service.getapp(i) for i in args.ref]
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
            if args.source is not None:
                sources = [self.service.getsource(s) for s in args.source]
            apps = self.service.local(None, ['U'], sources)
        runtimes = 0
        while (forcerun and runtimes == 0) or (apps is not None and len(apps) > 0):
            if not noconfirm and not specific and not forcerun:
                args.column = ['SOURCE', 'REF', 'NAME', 'AVAILABLE', 'INSTALLED']
                self._outputresults(apps, args)
                text = input("CONFIRM? [y/N]: ")
                if text.lower() != 'y':
                    sys.exit()
            apps = self.service.update(apps, noconfirm)
            if apps is not None and len(apps) > 0:
                print("WARNING: Some sources cannot only update specific apps, so the list of apps that will be updated has changed.")
            runtimes += 1

    def _outputresults(self, results, args):
        table = []
        header = args.column
        if header is None or len(header) == 0:
            header = self.default_columns
        columns = len(header)
        maxwidth = [len(header[i]) for i in range(0, columns)]
        as_csv = hasattr(args, 'csv') and args.csv
        noheader = hasattr(args, 'noheader') and args.noheader
        for sourceid in results.keys():
            for result in sorted(results[sourceid], key=lambda x: x.name.lower()):
                indicator = result.status()
                if not as_csv:
                    if indicator == 'N':
                        indicator = '   '
                    else:
                        indicator = "[{0}]".format(indicator)
                data = {
                    'STATUS': indicator,
                    'SOURCE': result.source.name,
                    'REF': self.service.make_superid(sourceid, result.id),
                    'NAME': result.name,
                    'AVAILABLE': (result.version if result.version is not None else '[Not Found]'),
                    'INSTALLED': (result.installed if result.installed is not None else ''),
                }
                if not as_csv:
                    for i in range(0, columns):
                        if len(data[header[i]]) > maxwidth[i]:
                            maxwidth[i] = len(data[header[i]])
                row = [data[h] for h in header]
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
                print(str.join(' ', [format(row[i], "<{0}".format(maxwidth[i])) for i in range(0, columns)]))

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
    cli.main()

if __name__ == '__main__':
    main()
