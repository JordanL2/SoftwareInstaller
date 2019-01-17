#!/usr/bin/python3

from softwareinstaller.app import App
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

    def search(self, name, statusfilter=None):
        if statusfilter == None:
            statusfilter = App.statuses
        results = {}
        for source in self.sources:
            sourceresults = source.search(name)
            sourceresults = [a for a in sourceresults if a.status() in statusfilter]
            if len(sourceresults) > 0:
                results[source.id] = sourceresults
        return results

    def local(self, name=None, statusfilter=None):
        if statusfilter == None:
            statusfilter = App.statuses
        results = {}
        for source in self.sources:
            sourceresults = source.local(name)
            sourceresults = [a for a in sourceresults if a.status() in statusfilter]
            if len(sourceresults) > 0:
                results[source.id] = sourceresults
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

    def update(self, apps, autoconfirm):
        for sourceid in apps.copy().keys():
            source = self.getsource(sourceid)
            updatedlist = source.update(apps[sourceid], autoconfirm)
            if updatedlist != None:
                apps[sourceid] = updatedlist
                return apps
            del apps[sourceid]
        return None

    def _split_superid(self, superid):
        i = superid.index(':')
        return (superid[0:i], superid[i + 1:])
