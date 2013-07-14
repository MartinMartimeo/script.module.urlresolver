#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#    urlresolver XBMC Addon
#    Copyright (C) 2011 t0mm0
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module provides the main API for accessing the urlresolver features.

For most cases you probably want to use :func:`urlresolver.resolve` or
:func:`urlresolver.choose_source`.

.. seealso::
    :class:`HostedMediaFile`

"""

# Logging
try:
    import common.addon

    log_debug = common.addon.log_debug
    log_error = common.addon.log_error
    get_setting = common.addon.get_setting
    plugins_path = common.addon.plugins_path
except ImportError:
    import logging

    log_debug = logging.debug
    log_error = logging.error
    get_setting = lambda key: None
    import os

    plugins_path = os.path.join(os.path.dirname(__file__), "plugins")

# Load classes
from types import HostedMediaFile

# Load xbmc unrelated functions
from util import resolve
from util import filter_source_list

# Try to load xbmc related functions aswell
try:
    from xutil import choose_source
    from xutil import display_settings
    from xutil import show_small_
except ImportError:
    choose_source = NotImplemented
    display_settings = NotImplemented

#load all available plugins
import plugnplay

plugnplay.set_plugin_dirs(plugins_path)
plugnplay.load_plugins()
