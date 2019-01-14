#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService

import sys

service = SoftwareService()

cmd = sys.argv[1]

if cmd == 'search':

	name = sys.argv[2]
	results = service.search(name)
	table = []
	columns = 6
	maxwidth = [0] * columns
	for sourceid in results.keys():
		for result in results[sourceid]:
			installed = '[    -    ]'
			if result.installed:
				installed = '[INSTALLED]'
			row = [installed, result.source.name, result.superid(), result.name, result.version, result.desc]
			for i in range(0, columns):
				if len(row[i]) > maxwidth[i]:
					maxwidth[i] = len(row[i])
			table.append(row)
	for row in table:
		print(str.join(' ', [format(row[i], "<{0}".format(maxwidth[i])) for i in range(0, columns)]))

elif cmd == 'show':

	superid = sys.argv[2]
	app = service.getapp(superid)
	print('Name:', app.name)
	print('Version:', app.version)
	print('Desc:', app.desc)
	print('Installed:', app.installed)

elif cmd == 'install':

	superid = sys.argv[2]
	service.install(superid)

elif cmd == 'remove':

	superid = sys.argv[2]
	service.remove(superid)

else:
	print("Unrecognised command '{0}'".format(cmd))
