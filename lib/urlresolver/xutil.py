#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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

import os
from urllib2 import HTTPError
import common
import plugnplay
from plugnplay.interfaces import PluginSettings
import xbmcgui

from urlresolver import filter_source_list


def choose_source(sources):
    """
    Given a list of :class:`HostedMediaFile` representing web pages that are
    thought to be associated with media content this function checks which are
    playable and if there are more than one it pops up a dialog box displaying
    the choices.

    Example::

        sources = [HostedMediaFile(url='http://youtu.be/VIDEOID', title='Youtube [verified] (20 views)'),
                   HostedMediaFile(url='http://putlocker.com/file/VIDEOID', title='Putlocker (3 views)')]
		source = urlresolver.choose_source(sources)
		if source:
			stream_url = source.resolve()
			addon.resolve_url(stream_url)
		else:
			addon.resolve_url(False)

    Args:
        sources (list): A list of :class:`HostedMediaFile` representing web
        pages that are thought to be associated with media content.

    Returns:
        The chosen :class:`HostedMediaFile` or ``False`` if the dialog is
        cancelled or none of the :class:`HostedMediaFile` are resolvable.

    """
    #get rid of sources with no resolver plugin
    try:
        sources = filter_source_list(sources)
    except HTTPError as e:
        error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')
        common.addon.log_error('got http error %d fetching %s' % (e.code, e.url))
        common.addon.show_small_popup(title='Error', msg='Http error: %s' % e, delay=8000, image=error_logo)
        return False
    except Exception as e:
        error_logo = os.path.join(common.addon_path, 'resources', 'images', 'redx.png')
        common.addon.log('**** Exception occured: %s' % e)
        common.addon.show_small_popup(title='[B][COLOR white]STAGEVU[/COLOR][/B]', msg='[COLOR red]%s[/COLOR]' % e,
                                      delay=5000, image=error_logo)
        return False

    #show dialog to choose source
    if len(sources) > 1:
        dialog = xbmcgui.Dialog()
        titles = []
        for source in sources:
            titles.append(source.title)
        index = dialog.select('Choose your stream', titles)
        if index > -1:
            return sources[index]
        else:
            return False

    #only one playable source so just play it
    elif len(sources) == 1:
        return sources[0]

    #no playable sources available
    else:
        common.addon.log_error('no playable streams found')
        return False


def display_settings():
    """
    Opens the settings dialog for :mod:`urlresolver` and its plugins.

    This can be called from your addon to provide access to global
    :mod:`urlresolver` settings. Each resolver plugin is also capable of
    exposing settings.

    .. note::

        All changes made to these setting by the user are global and will
        affect any addon that uses :mod:`urlresolver` and its plugins.
    """
    _update_settings_xml()
    common.addon.show_settings()


def _update_settings_xml():
    """
    This function writes a new ``resources/settings.xml`` file which contains
    all settings for this addon and its plugins.
    """
    try:
        try:
            os.makedirs(os.path.dirname(common.settings_file))
        except OSError:
            pass

        with open(common.settings_file, 'w') as f:
            f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
            f.write('<settings>\n')
            for imp in PluginSettings.implementors():
                f.write('<category label="%s">\n' % imp.name)
                f.write(imp.get_settings_xml())
                f.write('</category>\n')
            f.write('</settings>')
    except IOError:
        common.addon.log_error('error writing ' + common.settings_file)


#make sure settings.xml is up to date
_update_settings_xml()