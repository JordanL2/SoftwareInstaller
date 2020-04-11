#!/usr/bin/python3


class AbstractNotifier:

    def __init__(self, id):
        self.id = id

    # Checks if the notifier is installed and can be used.
    # Returns:
    #     True - Notifier can be used
    #     False - Notifier can NOT be used
    def testinstalled(self):
        raise Exception("Must override this method")

    # Sends notification that updates have been done
    def notify(self):
        raise Exception("Must override this method")
