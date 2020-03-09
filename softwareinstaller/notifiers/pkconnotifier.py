#!/usr/bin/python3

from softwareinstaller.abstractnotifier import AbstractNotifier
from softwareinstaller.commandexecutor import CommandExecutor


class PkconNotifier(AbstractNotifier):

    def __init__(self):
        self.executor = CommandExecutor()

    def testinstalled(self):
        return self.executor.call('which pkcon 2>/dev/null', None, None, None, [0, 1]) != ''

    def notify(self):
        return self.executor.call('pkcon refresh')
