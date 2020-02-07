#!/usr/bin/python3

from softwareinstaller.app import App

from softwareinstaller.sources.flatpaksource import FlatpakSource
from softwareinstaller.sources.pacmansource import PacmanSource
from softwareinstaller.sources.yaysource import YaySource

from softwareinstaller.notifiers.pkconnotifier import PkconNotifier


class SoftwareService:

    def __init__(self):
        allsources = [

            # Standard repo sources
            [
        	   PacmanSource(),
            ],

            # Arch AUR sources
            [
                YaySource(),
            ],

            # Flatpak sources
            [ 
                FlatpakSource(),
            ],
            
        ]
        self.sources = []
        for sourcegroup in allsources:
            for source in sourcegroup:
                if source.testinstalled():
                    self.sources.append(source)
                    break

        allnotifiers = [
            PkconNotifier(),
        ]
        self.notifiers = []
        for notifier in allnotifiers:
            if notifier.testinstalled():
                self.notifiers.append(notifier)

    def getsource(self, sourceid):
        for source in self.sources:
            if source.id == sourceid:
                return source
        return None

    def search(self, terms, statusfilter=None, sources=None):
        if statusfilter is None:
            statusfilter = App.statuses
        results = {}
        if sources is None:
            sources = self.sources
        for source in sources:
            source.refresh()
            sourceresults = source.search(terms)
            sourceresults = [a for a in sourceresults if a.status() in statusfilter]
            if len(sourceresults) > 0:
                results[source.id] = sourceresults
        return results

    def local(self, terms=None, statusfilter=None, sources=None):
        if statusfilter is None:
            statusfilter = App.statuses
        if sources is None:
            sources = self.sources
        results = {}
        for source in sources:
            source.refresh()
            sourceresults = source.local(terms)
            sourceresults = [a for a in sourceresults if a.status() in statusfilter]
            if len(sourceresults) > 0:
                results[source.id] = sourceresults
        return results

    def getapp(self, superid):
        sourceid, appid = self._split_superid(superid)
        source = self.getsource(sourceid)
        if source is None:
            raise Exception("No such sourceid")
        source.refresh()
        app = source.getapp(appid)
        if app is None:
            raise Exception("No such appid")
        return app

    def install(self, superid, user=False):
        app = self.getapp(superid)
        if app.isinstalled():
            raise Exception("App is already installed")
        app.user = user
        app.install()
        app = self.getapp(superid)
        if not app.isinstalled():
            raise Exception("App was not installed")
        
    def remove(self, superid):
        app = self.getapp(superid)
        if not app.isinstalled():
            raise Exception("App is not installed")
        app.remove()
        app = self.getapp(superid)
        if app.isinstalled():
            raise Exception("App was not removed")

    def update(self, apps, autoconfirm):
        for sourceid in apps.copy().keys():
            source = self.getsource(sourceid)
            updatedlist = source.update(apps[sourceid], autoconfirm)
            if updatedlist is not None:
                apps[sourceid] = updatedlist
                return apps
            
            if source.check_updated:
                apps_still_to_be_updated = self.local(None, ['U'], [source])
                if sourceid in apps_still_to_be_updated:
                    foundids = dict([(a.id, a.version) for a in apps_still_to_be_updated[sourceid]])
                    for app in apps[sourceid]:
                        if app.id in foundids and app.version == foundids[app.id]:
                            raise Exception("App {0} wasn't successfully updated".format(app.id))

            del apps[sourceid]

        for notifier in self.notifiers:
            notifier.notify()

        return None

    def _split_superid(self, superid):
        i = superid.index(':')
        return (superid[0:i], superid[i + 1:])
