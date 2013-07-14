#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0
    based on plugnplay by https://github.com/daltonmatos

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from glob import glob
from os.path import join, basename
import sys
from urlresolver import log_debug
from manager import *

__version__ = "0.1"

__all__ = ['Interface', 'Plugin']

man = Manager()

plugin_dirs = []


class Interface(object):
    """
        Marker for public interfaces
    """

    def __init__(self):
        super(Interface, self).__init__()

    @classmethod
    def implementors(cls):
        return man.implementors(cls)


class PluginMeta(type):
    def __new__(mcs, classname, bases, attrs):
        new_class = super(PluginMeta, mcs).__new__(mcs, classname, bases, attrs)

        new_class_instance = new_class()
        if attrs.has_key('implements'):
            for interface in attrs['implements']:
                man.add_implementor(interface, new_class_instance)
                log_debug('registering plugin: %s (%s), as: %s (P=%d)' % \
                          (new_class.name, new_class.__name__, interface.__name__,
                           new_class_instance.priority))

        return new_class


class Plugin(object):
    __metaclass__ = PluginMeta


def set_plugin_dirs(*dirs):
    for d in dirs:
        log_debug('adding plugin dir: %s' % d)
        plugin_dirs.append(d)


def load_plugins():
    for d in plugin_dirs:
        sys.path.append(d)
        py_files = glob(join(d, '*.py'))

        #Remove ".py" for proper importing
        modules = [basename(f[:-3]) for f in py_files]
        for mod_name in modules:
            imported_module = __import__(mod_name, globals(), locals())
            sys.modules[mod_name] = imported_module
