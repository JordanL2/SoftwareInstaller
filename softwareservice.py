#!/usr/bin/python3

from softwareinstaller.sources.flatpaksource import FlatpakSource
from softwareinstaller.sources.pacmansource import PacmanSource
from softwareinstaller.sources.yaourtsource import YaourtSource

class SoftwareService:

    def __init__(self):
        allsources = [
        	FlatpakSource(),
        	PacmanSource(),
            YaourtSource()
        ]
        self.sources = [s for s in allsources if s.testinstalled()]

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

    def local(self, name):
        results = {}
        for source in self.sources:
            results[source.id] = source.local(name)
        return results

    def getapp(self, superid):
        sourceid, appid = self._split_superid(superid)
        source = self.getsource(sourceid)
        if source == None:
            raise Exception("No such sourceid")
        app = source.getapp(appid)
        if app == None:
            raise Exception("No such appid")
        return app

    def install(self, superid):
        app = self.getapp(superid)
        if app.installed:
            raise Exception("App is already installed")
        app.install()
        app = self.getapp(superid)
        if not app.installed:
            raise Exception("App was not installed")
        
    def remove(self, superid):
        app = self.getapp(superid)
        if not app.installed:
            raise Exception("App is not installed")
        app.remove()
        app = self.getapp(superid)
        if app.installed:
            raise Exception("App was not removed")

    def _split_superid(self, superid):
        i = superid.index(':')
        return (superid[0:i], superid[i + 1:])
