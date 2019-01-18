#!/usr/bin/python3

from softwareinstaller.softwareservice import SoftwareService

import unittest

class TestSoftwareService(unittest.TestCase):

    def setUp(self):
        self.service = SoftwareService()
        self.service.testmode()


    # SEARCH

    def test_search(self):
        results = self.service.search('test')
        self.assertEqual(len(results['test']), 6)
        results = self.service.search('st5')
        self.assertFalse('test' in results)
        results = self.service.search('st6')
        self.assertEqual(len(results['test']), 1)

    def test_search_notinstalled(self):
        results = self.service.search('test', ['N'])
        self.assertEqual(len(results['test']), 2)

    def test_search_installed(self):
        results = self.service.search('test', ['I'])
        self.assertEqual(len(results['test']), 2)

    def test_search_update(self):
        results = self.service.search('test', ['U'])
        self.assertEqual(len(results['test']), 2)

    def test_search_I_and_U(self):
        results = self.service.search('test', ['I', 'U'])
        self.assertEqual(len(results['test']), 4)


    # LOCAL

    def test_local(self):
        results = self.service.local(None)
        self.assertEqual(len(results['test']), 5)
        results = self.service.local('st5')
        self.assertEqual(len(results['test']), 1)
        results = self.service.local('st6')
        self.assertFalse('test' in results)

    def test_local_notinstalled(self):
        results = self.service.local('test', ['N'])
        self.assertFalse('test' in results)

    def test_local_installed(self):
        results = self.service.local('test', ['I'])
        self.assertEqual(len(results['test']), 3)

    def test_local_update(self):
        results = self.service.local('test', ['U'])
        self.assertEqual(len(results['test']), 2)

    def test_local_I_and_U(self):
        results = self.service.local('test', ['I', 'U'])
        self.assertEqual(len(results['test']), 5)


    # GETAPP

    def test_getapp_installed(self):
        app = self.service.getapp('test:test1')
        self.assertEqual(app.name, 'Test1')
        self.assertEqual(app.version, '0.1')
        self.assertEqual(app.installed, '0.1')

    def test_getapp_not_installed(self):
        app = self.service.getapp('test:test6')
        self.assertEqual(app.name, 'Test6')
        self.assertEqual(app.version, '0.5')
        self.assertEqual(app.installed, '')

    def test_getapp_local_notremote(self):
        app = self.service.getapp('test:test5')
        self.assertEqual(app.name, 'Test5')
        self.assertEqual(app.version, '[Not Found]')
        self.assertEqual(app.installed, '0.3')

    def test_getapp_installed_update(self):
        app = self.service.getapp('test:test3')
        self.assertEqual(app.name, 'Test3')
        self.assertEqual(app.version, '0.2')
        self.assertEqual(app.installed, '0.1')

    def test_getapp_notfound(self):
        with self.assertRaises(Exception):
            app = self.service.getapp('test:wibble')


    # INSTALL

    def test_install_not_installed(self):
        self.assertFalse('test' in self.service.local('test6'))
        self.service.install('test:test6')
        self.assertEqual(self.service.local('test6')['test'][0].id, 'test6')

    def test_install_already_installed(self):
        with self.assertRaises(Exception):
            self.service.install('test:test1')

    def test_install_not_found(self):
        with self.assertRaises(Exception):
            self.service.install('test:wibble')


    # REMOVE

    def test_remove_installed(self):
        self.assertTrue('test' in self.service.local('test1'))
        self.service.remove('test:test1')
        self.assertFalse('test' in self.service.local('test1'))

    def test_remove_not_installed(self):
        with self.assertRaises(Exception):
            self.service.remove('test:test6')

    def test_remove_not_found(self):
        with self.assertRaises(Exception):
            self.service.remove('test:wibble')

    
    # UPDATE
    
    #TODO


if __name__ == '__main__':
    unittest.main()
