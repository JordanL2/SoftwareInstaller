#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService
from softwareinstaller.app import App

import sys


class SoftwareInstallerCLI:

	def __init__(self):
		self.service = SoftwareService()

	def do_command(self, cmd, args):
		flags_unparsed = [a for a in args if a.startswith('-')]
		args = [a for a in args if not a.startswith('-')]
		flags = {}
		for flag in flags_unparsed:
			if '=' in flag:
				key = flag[0:flag.index('=')]
				value = flag[flag.index('=') + 1:]
				flags[key] = value
			else:
				flags[flag] = True
		if '--test' in flags:
			self.service.testmode()
			print("BEGIN STATE")
			self._outputresults(self.service.local(None, None), flags)
			print("-----")

		if cmd == 'search':
			self.search(args, flags)
		elif cmd == 'local':
			self.local(args, flags)
		elif cmd == 'show':
			self.show(args, flags)
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
		if '--test' in flags:
			print("-----")
			print("END STATE")
			self._outputresults(self.service.local(None, None), flags)

	def help(self):
		print("search <NAME> [--csv] [--status=N,I,U]")
		print("local [<NAME>] [--csv] [--status=N,I,U]")
		print("show <REF>")
		print("install <REF>")
		print("remove <REF>")

	def search(self, args, flags):
		filters = self._get_status_flag(flags)
		name = args.pop(0)
		results = self.service.search(name, filters)
		self._outputresults(results, flags)

	def local(self, args, flags):
		filters = self._get_status_flag(flags)
		name = None
		if len(args) > 0:
			name = args.pop(0)
		results = self.service.local(name, filters)
		self._outputresults(results, flags)

	def show(self, args, flags):
		superid = args.pop(0)
		app = self.service.getapp(superid)
		print('Name:', app.name)
		print('Version:', app.version)
		print('Desc:', app.desc)
		if app.installed != '':
			print('Installed:', app.installed)

	def install(self, args, flags):
		superid = args.pop(0)
		self.service.install(superid)

	def remove(self, args, flags):
		superid = args.pop(0)
		self.service.remove(superid)

	def update(self, args, flags):
		autoconfirm = '-y' in flags
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
			apps = self.service.local(None, ['U'])
		while apps != None and len(apps) > 0:
			if not autoconfirm and not specific:
				self._outputresults(apps, flags)
				text = input("CONFIRM? [Y/n]: ")
				if text.lower() != 'y':
					sys.exit()
			apps = self.service.update(apps, autoconfirm)
			if apps != None and len(apps) > 0:
				print("WARNING: Some sources cannot only update specific apps, so the list of apps that will be updated has changed.")

	def _outputresults(self, results, flags):
		table = []
		columns = 7
		maxwidth = [0] * columns
		for sourceid in results.keys():
			for result in results[sourceid]:
				indicator = result.status()
				if indicator == 'N':
					indicator = ''
					if '--csv' not in flags:
						indicator = '   '
				else:
					indicator = "[{0}]".format(indicator)
				row = [indicator, result.source.name, result.superid(), result.name, result.version, result.installed, result.desc]
				if '--csv' not in flags:
					for i in range(0, columns):
						if len(row[i]) > maxwidth[i]:
							maxwidth[i] = len(row[i])
				table.append(row)
		if '--csv' in flags:
			for row in table:
				print(str.join(',', ["\"{0}\"".format(a) for a in row]))
		else:
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


cli = SoftwareInstallerCLI()
scriptpath = sys.argv.pop(0)
if len(sys.argv) == 0:
	cli.help()
else:
	cmd = sys.argv.pop(0)
	args = sys.argv.copy()
	cli.do_command(cmd, args)
