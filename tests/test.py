#!/usr/bin/python3

from softwareinstaller.app import App
from softwareinstaller.softwareservice import SoftwareService
from softwareinstaller.tests.testsource import TestSource

import unittest


class TestSoftwareService(unittest.TestCase):

    def setUp(self):
        self.service = SoftwareService()
        self.service.sources = [
            TestSource('test1', 'TestSource1'),
            TestSource('test2', 'TestSource2'),
        ]


    # SEARCH

    def test_search(self):
        results = self.service.search('app')
        self.assertEqual(len(results['test1']), 6)
        self.assertEqual(len(results['test2']), 6)

        results = self.service.search('pp5')
        self.assertFalse('test1' in results)
        self.assertFalse('test2' in results)

        results = self.service.search('pp6')
        self.assertEqual(len(results['test1']), 1)
        self.assertEqual(len(results['test2']), 1)

    def test_search_notinstalled(self):
        results = self.service.search('app', ['N'])
        self.assertEqual(len(results['test1']), 2)
        self.assertEqual(len(results['test2']), 2)

    def test_search_installed(self):
        results = self.service.search('app', ['I'])
        self.assertEqual(len(results['test1']), 2)
        self.assertEqual(len(results['test2']), 2)

    def test_search_update(self):
        results = self.service.search('app', ['U'])
        self.assertEqual(len(results['test1']), 2)
        self.assertEqual(len(results['test2']), 2)

    def test_search_I_and_U(self):
        results = self.service.search('app', ['I', 'U'])
        self.assertEqual(len(results['test1']), 4)
        self.assertEqual(len(results['test2']), 4)


    # LOCAL

    def test_local(self):
        results = self.service.local(None)
        self.assertEqual(len(results['test1']), 5)
        self.assertEqual(len(results['test2']), 5)

        results = self.service.local('pp5')
        self.assertEqual(len(results['test1']), 1)
        self.assertEqual(len(results['test2']), 1)

        results = self.service.local('pp6')
        self.assertFalse('test1' in results)
        self.assertFalse('test2' in results)

    def test_local_notinstalled(self):
        results = self.service.local('app', ['N'])
        self.assertFalse('test1' in results)

    def test_local_installed(self):
        results = self.service.local('app', ['I'])
        self.assertEqual(len(results['test1']), 3)
        self.assertEqual(len(results['test2']), 3)

    def test_local_update(self):
        results = self.service.local('app', ['U'])
        self.assertEqual(len(results['test1']), 2)
        self.assertEqual(len(results['test2']), 2)

    def test_local_I_and_U(self):
        results = self.service.local('app', ['I', 'U'])
        self.assertEqual(len(results['test1']), 5)
        self.assertEqual(len(results['test2']), 5)


    # GETAPP

    def test_getapp_installed(self):
        app = self.service.getapp('test1:app1')
        self.assertEqual(app.name, 'Test App 1')
        self.assertEqual(app.desc, 'Test1 desc')
        self.assertEqual(app.version, '0.1')
        self.assertEqual(app.installed, '0.1')

    def test_getapp_not_installed(self):
        app = self.service.getapp('test1:app6')
        self.assertEqual(app.name, 'Test App 6')
        self.assertEqual(app.desc, 'Test6 desc')
        self.assertEqual(app.version, '0.5')
        self.assertEqual(app.installed, '')

    def test_getapp_local_notremote(self):
        app = self.service.getapp('test1:app5')
        self.assertEqual(app.name, 'Test App 5')
        self.assertEqual(app.desc, 'Test5 desc')
        self.assertEqual(app.version, '[Not Found]')
        self.assertEqual(app.installed, '0.3')

    def test_getapp_installed_update(self):
        app = self.service.getapp('test1:app3')
        self.assertEqual(app.name, 'Test App 3')
        self.assertEqual(app.desc, 'Test3 desc')
        self.assertEqual(app.version, '0.2')
        self.assertEqual(app.installed, '0.1')

    def test_getapp_notfound(self):
        with self.assertRaises(Exception):
            app = self.service.getapp('test1:wibble')


    # INSTALL

    def test_install_not_installed(self):
        self.assertFalse('test1' in self.service.local('app6'))
        self.assertFalse('test2' in self.service.local('app6'))
        self.service.install('test1:app6')
        self.assertEqual(self.service.local('app6')['test1'][0].id, 'app6')
        self.assertFalse('test2' in self.service.local('app6'))

    def test_install_already_installed(self):
        with self.assertRaises(Exception):
            self.service.install('test:app1')

    def test_install_not_found(self):
        with self.assertRaises(Exception):
            self.service.install('test:wibble')


    # REMOVE

    def test_remove_installed(self):
        self.assertTrue('test1' in self.service.local('app1'))
        self.assertTrue('test2' in self.service.local('app1'))
        self.service.remove('test1:app1')
        self.assertFalse('test' in self.service.local('app1'))
        self.assertTrue('test2' in self.service.local('app1'))

    def test_remove_not_installed(self):
        with self.assertRaises(Exception):
            self.service.remove('test1:app6')

    def test_remove_not_found(self):
        with self.assertRaises(Exception):
            self.service.remove('test1:wibble')


    # UPDATE

    def test_update(self):
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        results = self.service.update(toupdate, False)
        self.assertIsNone(results)
        toupdate = self.service.local(None, ['U'])
        self.assertEqual(len(toupdate), 0)

    def test_update_listchanged1(self):
        self.service.sources[0] = TestSourceUpdateListChanges('test1', 'TestSource1')
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        results = self.service.update(toupdate, False)
        self.assertTrue('test1' in results)
        self.assertEqual(results['test1'][0].id, 'app4')
        self.assertTrue('test2' in results)

    def test_update_listchanged2(self):
        self.service.sources[1] = TestSourceUpdateListChanges('test2', 'TestSource2')
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        results = self.service.update(toupdate, False)
        self.assertFalse('test1' in results)
        self.assertTrue('test2' in results)
        self.assertEqual(results['test2'][0].id, 'app4')

    def test_update_listchanged_autoconfirm(self):
        self.service.sources[0] = TestSourceUpdateListChanges('test1', 'TestSource1')
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        results = self.service.update(toupdate, True)
        self.assertIsNone(results)

    def test_update_notupdated1(self):
        self.service.sources[0] = TestSourceUpdateFails('test1', 'TestSource1')
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        with self.assertRaises(Exception):
            results = self.service.update(toupdate, False)

    def test_update_notupdated2(self):
        self.service.sources[1] = TestSourceUpdateFails('test2', 'TestSource2')
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        with self.assertRaises(Exception):
            results = self.service.update(toupdate, False)

    def test_update_new_update_available(self):
        self.service.sources[0] = TestSourceNewUpdateAvailable('test1', 'TestSource1')
        toupdate = self.service.local(None, ['U'])
        self.assertTrue(len(toupdate) > 0)
        results = self.service.update(toupdate, False)
        self.assertIsNone(results)
        toupdate = self.service.local(None, ['U'])
        self.assertEqual(len(toupdate), 1)


class TestSourceUpdateListChanges(TestSource):

    def update(self, apps, autoconfirm):
        if not autoconfirm:
            return [App(self, 'app4', 'Test App 4', 'Test4 desc', '0.5', '0.3'),]
        for app in apps:
            if app.id not in self.remote:
                raise Exception("Could not update {0} - not available in remote")
            self.installed[app.id].installed = self.remote[app.id].version
        return None


class TestSourceUpdateFails(TestSource):

    def update(self, apps, autoconfirm):
        return None


class TestSourceNewUpdateAvailable(TestSource):

    def update(self, apps, autoconfirm):
        for app in apps:
            if app.id not in self.remote:
                raise Exception("Could not update {0} - not available in remote")
            self.installed[app.id].installed = self.remote[app.id].version
        self.remote[apps[0].id].version = '1.0'
        return None


if __name__ == '__main__':
    unittest.main()
