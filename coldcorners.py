#!/usr/bin/env python3

from argparse import ArgumentParser
from configparser import ConfigParser
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Gio, Notify

import os


VERSION = (0, 0, 1)
__version__ = '.'.join(map(str, VERSION))


def plugin(plugin):

    schema = 'org.compiz.{}'.format(plugin)
    path = '/org/compiz/profiles/unity/plugins/{}/'.format(plugin)

    return Gio.Settings(schema=schema,  path=path)


class Config(object):

    def __init__(self):

        defaults = {
            'default': {
                'saved': False,
            },
            'hotcorners': {
                'show-desktop-edge': '',
                'expo-edge': '',
                'initiate-edge': '',
                'initiate-all-edge': '',
            }
        }

        self.files = [
            'coldcorners.cfg',
            os.path.expanduser('~/.coldcorners.cfg'),
        ]

        self.parser = ConfigParser()

        self.parser.read_dict(defaults)
        self.parser.read(self.files)

        if self.parser.has_section('hotcorners'):
            self.hotcorners = self.parser['hotcorners']
        else:
            self.parser.add_section('hotcorners')
            self.hotcorners = self.parser['hotcorners']

    def write(self):

        with open(self.files[-1], 'w') as f:
            self.parser.write(f)

    @property
    def saved(self):
        return self.parser.getboolean('default', 'saved', fallback=False)

    @saved.setter
    def saved(self, value):
        if value is True:
            value = 'on'
        elif value is False:
            value = 'off'

        self.parser.set('default', 'saved', value)
        self.write()

    @property
    def show_desktop_edge(self):
        return str(self.hotcorners['show-desktop-edge'])

    @show_desktop_edge.setter
    def show_desktop_edge(self, value):
        self.hotcorners['show-desktop-edge'] = value
        self.write()

    @property
    def expo_edge(self):
        return str(self.hotcorners['expo-edge'])

    @expo_edge.setter
    def expo_edge(self, value):
        self.hotcorners['expo-edge'] = value
        self.write()

    @property
    def initiate_edge(self):
        return str(self.hotcorners['initiate-edge'])

    @initiate_edge.setter
    def initiate_edge(self, value):
        self.hotcorners['initiate-edge'] = value
        self.write()

    @property
    def initiate_all_edge(self):
        return str(self.hotcorners['initiate-all-edge'])

    @initiate_all_edge.setter
    def initiate_all_edge(self, value):
        self.hotcorners['initiate-all-edge'] = value
        self.write()


class ColdCorners(object):

    def __init__(self, config, notification=False):

        self.cfg = config
        self.core = plugin('core')
        self.expo = plugin('expo')
        self.scale = plugin('scale')
        self.notif = notification

        Notify.init('coldcorners')

    def out(self, message):

        if self.notif:
            notif = Notify.Notification.new('ColdCorners', message, '')
            notif.show()

        else:
            print(message)

    def enable(self):

        if self.cfg.saved:

            self.core.set_string('show-desktop-edge',
                                 self.cfg.show_desktop_edge)
            self.core.sync()
            self.expo.set_string('expo-edge', self.cfg.expo_edge)
            self.expo.sync()

            self.scale.set_string('initiate-edge', self.cfg.initiate_edge)
            self.scale.set_string('initiate-all-edge',
                                  self.cfg.initiate_all_edge)
            self.scale.sync()

            self.cfg.saved = False
            self.out('Enable success!')
        else:
            self.out('Cannot enable, hotcorners never been disabled before!')

    def disable(self):

        if self.cfg.saved:
            self.out('Cannot disable, hotcorners has been disabled before!')
        else:
            self.cfg.show_desktop_edge = self.core.get_string(
                'show-desktop-edge'
            )
            self.cfg.expo_edge = self.expo.get_string('expo-edge')
            self.cfg.initiate_edge = self.scale.get_string('initiate-edge')
            self.cfg.initiate_all_edge = self.scale.get_string(
                'initiate-all-edge'
            )

            self.core.set_string('show-desktop-edge', '')
            self.core.sync()

            self.expo.set_string('expo-edge', '')
            self.expo.sync()

            self.scale.set_string('initiate-edge', '')
            self.scale.set_string('initiate-all-edge', '')
            self.scale.sync()

            self.cfg.saved = True

            self.out('Disable success!')

    def toggle(self):

        if self.cfg.saved:
            self.enable()
        else:
            self.disable()


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('command', help='enable/disable/toggle hotcorners',
                        choices=['enable', 'disable', 'toggle'], nargs='?')
    parser.add_argument('-n', '--notification', help='show notification',
                        action='store_true', required=False)
    args = parser.parse_args()

    coldcorners = ColdCorners(Config(), args.notification)

    if args.command == 'enable':
        coldcorners.enable()
    elif args.command == 'disable':
        coldcorners.disable()
    elif args.command == 'toggle':
        coldcorners.toggle()
    else:
        parser.print_help()
