#!/usr/bin/python3

from softwareinstaller.app import App

from softwareinstaller.commandexecutor import CommandExecutor

from softwareinstaller.sources.flatpaksource import FlatpakSource
from softwareinstaller.sources.pacmansource import PacmanSource
from softwareinstaller.sources.yaysource import YaySource


class SoftwareService:

    def __init__(self):
        self.executor = CommandExecutor()

        self.allsources = [

            # Standard repo sources
            [
        	   PacmanSource(self),
            ],

            # Arch AUR sources
            [
                YaySource(self),
            ],

            # Flatpak sources
            [ 
                FlatpakSource(self),
            ],
            
        ]
        self.sources = []

        self.default_config()

        self.output_std = None
        self.output_err = None
        self.output_log = {}

        self.debug = {
            'performance': False
        }

    def default_config(self):
        self.config_options = {
            'ref.delimiter': [str, ':'],
            'sources.autodetect': [bool, True],
            'install.tasks.pre': [list, []],
            'install.tasks.post': [list, []],
            'remove.tasks.pre': [list, []],
            'remove.tasks.post': [list, []],
            'update.tasks.pre': [list, []],
            'update.tasks.post': [list, []],
        }

        for sourcegroup in self.allsources:
            for source in sourcegroup:
                for k, v in source.config_options.items():
                    self.config_options["sources.{}.{}".format(source.id, k)] = v

        self.config = dict([(k, v[1]) for k, v in self.config_options.items()])

    def load_sources(self):
        if self.config['sources.autodetect']:
            for sourcegroup in self.allsources:
                for source in sourcegroup:
                    config_id = "sources.{}.enable".format(source.id)
                    if self.config[config_id] != False:
                        if source.testinstalled():
                            self.sources.append(source)
                            break
        else:
            for sourcegroup in self.allsources:
                for source in sourcegroup:
                    config_id = "sources.{}.enable".format(source.id)
                    if config_id in self.config and self.config[config_id]:
                        self.sources.append(source)

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
        sourceid, appid = self.split_superid(superid)
        source = self.getsource(sourceid)
        if source is None:
            raise Exception("No such sourceid")
        source.refresh()
        app = source.getapp(appid)
        if app is None:
            raise Exception("No such appid")
        return app

    def install(self, superid, user=False, system=False):
        app = self.getapp(superid)
        if app.isinstalled():
            raise Exception("App is already installed")
        if user:
            app.user = True
        elif system:
            app.user = False
        else:
            app.user = None

        for task in self.config['install.tasks.pre']:
            self.log("\n*** INSTALL PRE TASK: {} ***".format(task))
            self.executor.call(task, stdout=self.output_std, stderr=self.output_err)
        
        self.log("\n*** INSTALL APP: {} ***".format(superid))
        app.install()

        app = self.getapp(superid)
        if not app.isinstalled():
            raise Exception("App was not installed")

        for task in self.config['install.tasks.post']:
            self.log("\n*** INSTALL POST TASK: {} ***".format(task))
            self.executor.call(task, stdout=self.output_std, stderr=self.output_err)
        
    def remove(self, superid):
        app = self.getapp(superid)
        if not app.isinstalled():
            raise Exception("App is not installed")

        for task in self.config['remove.tasks.pre']:
            self.log("\n*** REMOVE PRE TASK: {} ***".format(task))
            self.executor.call(task, stdout=self.output_std, stderr=self.output_err)

        self.log("\n*** REMOVE APP: {} ***".format(superid))
        app.remove()

        app = self.getapp(superid)
        if app.isinstalled():
            raise Exception("App was not removed")

        for task in self.config['remove.tasks.post']:
            self.log("\n*** REMOVE POST TASK: {} ***".format(task))
            self.executor.call(task, stdout=self.output_std, stderr=self.output_err)

    def update(self, apps, autoconfirm):
        for task in self.config['update.tasks.pre']:
            self.log("\n*** UPDATE PRE TASK: {} ***".format(task))
            self.executor.call(task, stdout=self.output_std, stderr=self.output_err)

        for sourceid in apps.copy().keys():
            source = self.getsource(sourceid)
            self.log("\n*** UPDATE SOURCE: {} ***".format(source.name))
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

        for task in self.config['update.tasks.post']:
            self.log("\n*** UPDATE POST TASK: {} ***".format(task))
            self.executor.call(task, stdout=self.output_std, stderr=self.output_err)

        return None

    def log(self, message):
        if self.output_std is not None:
            print(message, file=self.output_std)

    def make_superid(self, source_id, app_id):
        return source_id + self.config['ref.delimiter'] + app_id

    def split_superid(self, superid):
        i = superid.index(self.config['ref.delimiter'])
        return (superid[0:i], superid[i + 1:])
