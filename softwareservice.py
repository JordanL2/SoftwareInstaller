#!/usr/bin/python3

from softwareinstaller.sources.flatpaksource import FlatpakSource
from softwareinstaller.sources.pacmansource import PacmanSource

class SoftwareService:

    def __init__(self):
        all_sources = [
        	FlatpakSource(),
        	PacmanSource()
        ]
        self.sources = [s for s in all_sources if s.test_installed()]

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

    def getapp(self, superid):
        sourceid, appid = self._split_super_id(superid)
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
        
    def remove(self, superid):
        app = self.getapp(superid)
        if not app.installed:
            raise Exception("App is not installed")
        app.remove()

    def _split_super_id(self, superid):
        i = superid.index(':')
        return (superid[0:i], superid[i + 1:])
