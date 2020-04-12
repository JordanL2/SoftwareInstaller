#!/usr/bin/python3

from softwareinstaller.app import App


class AbstractSource:

    def __init__(self, service, id, name):
        self.service = service
        # Human readable identifer for the source, no spaces, preferably lowercase
        self.id = id
        # Nicely formatted title for the source
        self.name = name
        # After a source's apps are updated, it's checked that the correct version is now installed
        self.check_updated = True

    # Checks if the source is installed and can be used.
    # Returns:
    #     True - Source can be used
    #     False - Source can NOT be used
    def testinstalled(self):
        raise Exception("Must override this method")

    # Refreshes the list of remotely available apps
    def refresh(self):
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
