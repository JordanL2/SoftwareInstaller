#!/usr/bin/python3

from softwareinstaller.app import App

import subprocess

class AbstractSource:

    def __init__(self, id, name):
        self.id = id
        self.name = name

    def test_installed(self):
        raise Exception("Must override this method")

    def search(self, name):
        raise Exception("Must override this method")

    def local(self, name):
        raise Exception("Must override this method")

    def getapp(self, appid):
        raise Exception("Must override this method")

    def install(self, app):
        raise Exception("Must override this method")

    def remove(self, app):
        raise Exception("Must override this method")

    def call(self, command, regex=None, converters=None, ignorenomatch=False, successcodes=None):
        if successcodes == None:
            successcodes = [0]
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.decode('utf-8').rstrip("\n")
        stderr = result.stderr.decode('utf-8').rstrip("\n")
        if result.returncode not in successcodes:
            raise Exception("Command: {0}\nReturn Code: {1}\nStandard Output: {2}\nError Output: {3}".format(command, result.returncode, stdout, stderr))
        if regex is None:
            return stdout
        response = []
        for line in stdout.splitlines():
            match = regex.match(line)
            if match:
                result_line = match.groups()
                if converters is not None:
                    result_line = [converters[i](r) for i, r in enumerate(result_line)]
                response.append(result_line)
            elif not ignorenomatch:
                raise Exception("Line '{0}' did not match regex".format(line))
        return response
