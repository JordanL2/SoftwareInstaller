#!/usr/bin/python3

from softwareinstaller.sources.flatpaksource import FlatpakSource
from softwareinstaller.tests.testcommandexecutor import TestCommandExecutor

import unittest


class TestFlatpakSource(unittest.TestCase):

    def setUp(self):
        self.source = FlatpakSource()
        self.source.executor = TestCommandExecutor({
                
                'flatpak list --columns=version,description,application,origin': '''
cmp app/com.sublimetext.three/x86_64/stable app/org.gimp.GIMP/x86_64/stable
cmp app/org.supertuxproject.SuperTux/x86_64/stable runtime/org.freedesktop.Platform.html5-codecs/x86_64/18.08
cmp app/org.kde.krita/x86_64/stable runtime/org.freedesktop.Platform.html5-codecs/x86_64/18.08
cmp app/org.kde.krita/x86_64/stable app/org.supertuxproject.SuperTux/x86_64/stable
cmp app/com.sublimetext.three/x86_64/stable runtime/org.freedesktop.Platform.html5-codecs/x86_64/18.08
cmp app/org.gimp.GIMP/x86_64/stable runtime/org.freedesktop.Platform.html5-codecs/x86_64/18.08
cmp app/org.gimp.GIMP/x86_64/stable app/org.kde.krita/x86_64/stable
cmp runtime/org.freedesktop.Platform/x86_64/18.08 runtime/org.freedesktop.Sdk/x86_64/18.08
cmp runtime/org.gtk.Gtk3theme.Breeze-Dark/x86_64/3.22 runtime/org.kde.Platform/x86_64/5.11
cmp runtime/org.gnome.Platform/x86_64/3.28 runtime/org.gtk.Gtk3theme.Breeze-Dark/x86_64/3.22
cmp runtime/org.freedesktop.Platform/x86_64/18.08 runtime/org.gnome.Platform/x86_64/3.28
cmp runtime/org.freedesktop.Sdk/x86_64/18.08 runtime/org.gnome.Platform/x86_64/3.28
cmp app/com.sublimetext.three/x86_64/stable runtime/org.freedesktop.Platform/x86_64/18.08
cmp runtime/org.freedesktop.Platform.html5-codecs/x86_64/18.08 runtime/org.freedesktop.Platform/x86_64/18.08
cmp runtime/org.freedesktop.Platform.html5-codecs/x86_64/18.08 runtime/org.freedesktop.Sdk/x86_64/18.08
cmp app/org.gimp.GIMP/x86_64/stable runtime/org.freedesktop.Sdk/x86_64/18.08
cmp app/org.gimp.GIMP/x86_64/stable runtime/org.gnome.Platform/x86_64/3.28
cmp app/org.kde.krita/x86_64/stable runtime/org.gnome.Platform/x86_64/3.28
cmp app/org.kde.krita/x86_64/stable runtime/org.gtk.Gtk3theme.Breeze-Dark/x86_64/3.22
cmp app/org.kde.krita/x86_64/stable runtime/org.kde.Platform/x86_64/5.11
Version                         Description                                                                                                                                                                 Application                                                 Origin
3.1.1                           Sublime Text - Sophisticated text editor for code, markup and prose                                                                                                         com.sublimetext.three                                       flathub
                                Freedesktop.org Application Platform version 18.08 - Shared libraries provided by freedesktop.org                                                                           org.freedesktop.Platform                                    flathub
                                html5-codecs                                                                                                                                                                org.freedesktop.Platform.html5-codecs                       flathub
                                Freedesktop.org Software Development Kit version 18.08 - Tools and headers for developing applications using the freedesktop.org application platform                       org.freedesktop.Sdk                                         flathub
2.10.7                          GNU Image Manipulation Program - Create images and edit photographs                                                                                                         org.gimp.GIMP                                               flathub
                                GNOME Application Platform version 3.28 - Shared libraries used by GNOME applications                                                                                       org.gnome.Platform                                          flathub
                                Breeze Gtk theme - Breeze Gtk theme matching the KDE Breeze theme                                                                                                           org.gtk.Gtk3theme.Breeze-Dark                               flathub
                                KDE Application Platform version master - Shared libraries used by KDE applications                                                                                         org.kde.Platform                                            flathub
4.1.7.101                       Krita - Digital Painting, Creative Freedom                                                                                                                                  org.kde.krita                                               flathub
0.6.0                           SuperTux - A jump-and-run game starring Tux the Penguin                                                                                                                     org.supertuxproject.SuperTux                                flathub
''',
                
                'flatpak search "gimp" --columns=version,description,application,remotes': '''
Version Description                                                         Application            Remotes
2.10.8  GNU Image Manipulation Program - Create images and edit photographs org.gimp.GIMP          flathub
0.0.8   Scans to PDF - Create small, searchable PDFs from scanned documents com.github.unrud.djpdf flathub
''',

                'flatpak search "org.gimp.GIMP" --columns=version,description,application,remotes': '''
Version Description                                                         Application   Remotes
2.10.8  GNU Image Manipulation Program - Create images and edit photographs org.gimp.GIMP flathub
''',

                'flatpak search "org.kde.krita" --columns=version,description,application,remotes': '''
No matches found
''',

            })


    # SEARCH

    def test_search(self):
        results = self.source.search('gimp')
        self.assertEqual(len(results), 2)

        self.assertEqual(results[0].id, 'flathub:org.gimp.GIMP')
        self.assertEqual(results[0].name, 'GNU Image Manipulation Program')
        self.assertEqual(results[0].desc, 'Create images and edit photographs')
        self.assertEqual(results[0].version, '2.10.8')
        self.assertEqual(results[0].installed, '2.10.7')

        self.assertEqual(results[1].id, 'flathub:com.github.unrud.djpdf')
        self.assertEqual(results[1].name, 'Scans to PDF')
        self.assertEqual(results[1].desc, 'Create small, searchable PDFs from scanned documents')
        self.assertEqual(results[1].version, '0.0.8')
        self.assertEqual(results[1].installed, None)


    # LOCAL

    def test_local(self):
        results = self.source.local('gimp')
        self.assertEqual(len(results), 1)

        self.assertEqual(results[0].id, 'flathub:org.gimp.GIMP')
        self.assertEqual(results[0].name, 'GNU Image Manipulation Program')
        self.assertEqual(results[0].desc, 'Create images and edit photographs')
        self.assertEqual(results[0].version, '2.10.8')
        self.assertEqual(results[0].installed, '2.10.7')

    def test_local_notremote(self):
        results = self.source.local('krita')
        self.assertEqual(len(results), 1)

        self.assertEqual(results[0].id, 'flathub:org.kde.krita')
        self.assertEqual(results[0].name, 'Krita')
        self.assertEqual(results[0].desc, 'Digital Painting, Creative Freedom')
        self.assertEqual(results[0].version, None)
        self.assertEqual(results[0].installed, '4.1.7.101')


if __name__ == '__main__':
    unittest.main()
