#!/usr/bin/python3

from softwareinstaller.app import App

import subprocess


class AbstractSource:

    def __init__(self, id, name):
        # Human readable identifer for the source, no spaces, preferably lowercase
        self.id = id
        # Nicely formatted title for the source
        self.name = name

    # Checks if the source is installed and can be used.
    # Returns:
    #     True - Source can be used
    #     False - Source can NOT be used
    def testinstalled(self):
        raise Exception("Must override this method")

    # Searches remote source for apps matching a string
    # Input:
    #     name - string to match
    # Returns:
    #     list of App instances
    def search(self, name):
        raise Exception("Must override this method")

    # Searches locally installed packages from this source for apps matching a string
    # Input:
    #     name - string to match, if None then return all locally installed packages from this source
    # Returns:
    #     list of App instances
    def local(self, name):
        raise Exception("Must override this method")

    # Gets info about a specific app. This should work whether the app is installed or not, and whether it's in the remote source or not.
    # Input:
    #     appid - id of the app required
    # Returns:
    #     App instance
    def getapp(self, appid):
        raise Exception("Must override this method")

    # Installs a specific app
    # Input:
    #     app - App instance to be installed
    def install(self, app):
        raise Exception("Must override this method")

    # Uninstalls a specific app
    # Input:
    #     app - App instance to be installed
    def remove(self, app):
        raise Exception("Must override this method")

    # Updates the given list of apps. If the source cannot only update specific apps, and the list of apps that will be updated has changed:
    #     If autoconfirm, just update everything
    #     Else, return the new list of apps the source will update
    # Input:
    #     apps - list of App instances to update
    #     autoconfirm - boolean, if true, don't bother checking if the list of apps matches the list that will be updated
    # Returns:
    #     list of App instances if the list has changed, otherwise None
    def update(self, apps, autoconfirm):
        raise Exception("Must override this method")

    def _call(self, command, regex=None, converters=None, ignorenomatch=False, successcodes=0):
        if successcodes == 0:
            successcodes = [0]
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = result.stdout.decode('utf-8').rstrip("\n")
        stderr = result.stderr.decode('utf-8').rstrip("\n")
        if successcodes is not None and result.returncode not in successcodes:
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
