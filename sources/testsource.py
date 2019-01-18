#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re


class TestSource(AbstractSource):

    def __init__(self):
        super().__init__('test', 'TestSource')
        self.installed = dict([(a.id, a) for a in [
            App(self, 'test1', 'Test1', 'Test1 desc', '0.1', '0.1'),
            App(self, 'test2', 'Test2', 'Test2 desc', '0.2', '0.2'),
            App(self, 'test3', 'Test3', 'Test3 desc', '0.2', '0.1'),
            App(self, 'test4', 'Test4', 'Test4 desc', '0.4', '0.3'),
            App(self, 'test5', 'Test5', 'Test5 desc', None, '0.3'),
        ]])
        self.remote = dict([(a.id, a) for a in [
            App(self, 'test1', 'Test1', 'Test1 desc', '0.1', None),
            App(self, 'test2', 'Test2', 'Test2 desc', '0.2', None),
            App(self, 'test3', 'Test3', 'Test3 desc', '0.2', None),
            App(self, 'test4', 'Test4', 'Test4 desc', '0.4', None),
            App(self, 'test6', 'Test6', 'Test6 desc', '0.5', None),
            App(self, 'test7', 'Test7', 'Test7 desc', '0.6', None),
        ]])

    def testinstalled(self):
        return True

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
            if name == None or app.match(name):
                remoteapp = self.getapp(app.id)
                app.version = remoteapp.version
                results.append(app)
        return results

    def getapp(self, appid, installed=None):
        app = None
        if appid in self.installed:
            app = self.installed[appid].copy()
            app.version = '[Not Found]'
        if appid in self.remote:
            remoteapp = self.remote[appid]
            if app == None:
                remoteapp.installed = ''
                return remoteapp.copy()
            else:
                app.version = remoteapp.version
        return app

    def install(self, app):
        self.installed[app.id] = app.copy()
        app.installed = app.version

    def remove(self, app):
        del self.installed[app.id]

    def update(self, apps, autoconfirm):
        for app in apps:
            if app.id not in self.remote:
                raise Exception("Could not update {0} - not available in remote")
            self.installed[app.id].installed = self.remote[app.id].version
            self.remote[app.id].version = '1.0'
        return None
