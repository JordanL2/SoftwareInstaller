#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService

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
		else:
			print("Unrecognised command '{0}'".format(cmd))

	def search(self, args, flags):
		name = args.pop(0)
		results = self.service.search(name)
		self._outputresults(results, flags)

	def local(self, args, flags):
		name = None
		if len(args) > 0:
			name = args.pop(0)
		results = self.service.local(name)
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

	def _outputresults(self, results, flags):
		defaultfilters = ['N', 'I', 'U']
		filters = defaultfilters.copy()
		if '--status' in flags:
			filters = flags['--status'].split(',')
			for filter in filters:
				if filter not in defaultfilters:
					raise Exception("Unrecognised filter: {0}".format(filter))

		table = []
		columns = 7
		maxwidth = [0] * columns
		for sourceid in results.keys():
			for result in results[sourceid]:
				indicator = result.status()
				if ((indicator == 'N'  and 'N' not in filters)
				 or (indicator == 'I' and 'I' not in filters)
				 or (indicator == 'U' and 'U' not in filters)):
					continue
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


cli = SoftwareInstallerCLI()
scriptpath = sys.argv.pop(0)
cmd = sys.argv.pop(0)
args = sys.argv.copy()
cli.do_command(cmd, args)
