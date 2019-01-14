#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService

import sys

service = SoftwareService()

cmd = sys.argv[1]

if cmd == 'search':

	name = sys.argv[2]
	results = service.search(name)
	table = []
	columns = 5
	maxwidth = [0] * columns
	for sourceid in results.keys():
		for result in results[sourceid]:
			installed = '[    -    ]'
			if result.installed:
				installed = '[INSTALLED]'
			row = [installed, sourceid, result.id, result.name, result.desc]
			for i in range(0, columns):
				if len(row[i]) > maxwidth[i]:
					maxwidth[i] = len(row[i])
			table.append(row)
	for row in table:
		print(str.join(' ', [format(row[i], "<{0}".format(maxwidth[i])) for i in range(0, columns)]))

elif cmd == 'show':

	sourceid = sys.argv[2]
	appid = sys.argv[3]
	app = service.getapp(sourceid, appid)
	print('Name:', app.name)
	print('Desc:', app.desc)
	print('Installed:', app.installed)

elif cmd == 'install':

	sourceid = sys.argv[2]
	appid = sys.argv[3]
	service.install(sourceid, appid)

elif cmd == 'remove':

	sourceid = sys.argv[2]
	appid = sys.argv[3]
	service.remove(sourceid, appid)

else:
	print("Unrecognised command '{0}'".format(cmd))
