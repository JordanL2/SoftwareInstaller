#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService

import sys

service = SoftwareService()

cmd = sys.argv[1]

if cmd == 'search':

	name = sys.argv[2]
	results = service.search(name)
	for sourceid in results.keys():
		for result in results[sourceid]:
			print(sourceid, '|', result.id, '|', result.name, '|', result.desc)

elif cmd == 'show':

	sourceid = sys.argv[2]
	appid = sys.argv[3]
	app = service.show(sourceid, appid)
	print('Name:', app.name)
	print('Desc:', app.desc)

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
