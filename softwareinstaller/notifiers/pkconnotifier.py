#!/usr/bin/python3

from softwareinstaller.abstractnotifier import AbstractNotifier
from softwareinstaller.commandexecutor import CommandExecutor


class PkconNotifier(AbstractNotifier):

    def __init__(self, service):
        super().__init__(service, 'pkcon')
        self.executor = CommandExecutor()

    def testinstalled(self):
        return self.executor.call('which pkcon 2>/dev/null', None, None, None, [0, 1]) != ''

    def notify(self):
        return self.executor.call('pkcon refresh', stdout=self.service.output_std, stderr=self.service.output_err)
