#!/usr/bin/python3

from softwareinstaller.sources.flatpaksource import FlatpakSource

class SoftwareService:

	def __init__(self):
		self.sources = [
			FlatpakSource()
		]

	def getsource(self, sourceid):
		for source in self.sources:
			if source.id == sourceid:
				return source
		return None

	def search(self, name):
		results = {}
		for source in self.sources:
			results[source.id] = source.search(name)
		return results

	def getapp(self, sourceid, appid):
		source = self.getsource(sourceid)
		if source == None:
			raise Exception("No such sourceid")
		app = source.getapp(appid)
		if app == None:
			raise Exception("No such appid")
		return app

	def install(self, sourceid, appid):
		app = self.getapp(sourceid, appid)
		if app.installed():
			raise Exception("App is already installed")
		app.install()
		
	def remove(self, sourceid, appid):
		app = self.getapp(sourceid, appid)
		if not app.installed():
			raise Exception("App is not installed")
		app.remove()
