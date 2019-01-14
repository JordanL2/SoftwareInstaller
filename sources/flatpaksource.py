#!/usr/bin/python3

from softwareinstaller.abstractsource import *

import re
import subprocess

class FlatpakSource(AbstractSource):

    search_regex = re.compile(r'^(.+?)\s+\-\s+(.+)\s+(\S+)$')

    def __init__(self):
        super().__init__('flatpak', 'Flatpak')

    def search(self, name):
        table = self.call("flatpak search {0}  --columns=description,application".format(name), self.search_regex)
        results = []
        for row in table:
            results.append(App(self, row[2], row[0], row[1]))
        return results

    def getapp(self, appid):
        #TODO
        pass

    def installapp(self, app):
        #TODO
        pass

    def removeapp(self, app):
        #TODO
        pass
    
    def installed(self, app):
        #TODO
        pass
