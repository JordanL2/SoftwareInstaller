#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re


class TestSource(AbstractSource):

    def __init__(self, id='test', name='TestSource'):
        super().__init__(id, name)
        self.installed = dict([(a.id, a) for a in [
            App(self, 'app1', 'Test App 1', 'Test1 desc', '0.1', '0.1', False),
            App(self, 'app2', 'Test App 2', 'Test2 desc', '0.2', '0.2', False),
            App(self, 'app3', 'Test App 3', 'Test3 desc', '0.2', '0.1', False),
            App(self, 'app4', 'Test App 4', 'Test4 desc', '0.4', '0.3', False),
            App(self, 'app5', 'Test App 5', 'Test5 desc', None, '0.3', False),
        ]])
        self.remote = dict([(a.id, a) for a in [
            App(self, 'app1', 'Test App 1', 'Test1 desc', '0.1', None, False),
            App(self, 'app2', 'Test App 2', 'Test2 desc', '0.2', None, False),
            App(self, 'app3', 'Test App 3', 'Test3 desc', '0.2', None, False),
            App(self, 'app4', 'Test App 4', 'Test4 desc', '0.4', None, False),
            App(self, 'app6', 'Test App 6', 'Test6 desc', '0.5', None, False),
            App(self, 'app7', 'Test App 7', 'Test7 desc', '0.6', None, False),
        ]])

    def testinstalled(self):
        return True

    def refresh(self):
        pass

    def search(self, name):
        results = []
        for app in self.remote.values():
            app = app.copy()
            if app.match(name):
                localapp = self.getapp(app.id)
                app.installed = localapp.installed
                results.append(app)
        return results

    def local(self, name):
        results = []
        for app in self.installed.values():
            app = app.copy()
            if name is None or app.match(name):
                remoteapp = self.getapp(app.id)
                app.version = remoteapp.version
                results.append(app)
        return results

    def getapp(self, appid, installed=None):
        app = None
        if appid in self.installed:
            app = self.installed[appid].copy()
            app.version = None
        if appid in self.remote:
            remoteapp = self.remote[appid]
            if app is None:
                remoteapp.installed = None
                return remoteapp.copy()
            else:
                app.version = remoteapp.version
        return app

    def install(self, app):
        app = app.copy()
        self.installed[app.id] = app
        app.installed = app.version

    def remove(self, app):
        del self.installed[app.id]

    def update(self, apps, autoconfirm):
        for app in apps:
            if app.id not in self.remote:
                raise Exception("Could not update {0} - not available in remote")
            self.installed[app.id].installed = self.remote[app.id].version
        return None
