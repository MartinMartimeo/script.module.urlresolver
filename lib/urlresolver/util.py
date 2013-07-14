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
from types import HostedMediaFile


def resolve(web_url):
    """
    Resolve a web page to a media stream.

    It is usually as simple as::

        import urlresolver
        media_url = urlresolver.resolve(web_url)

    where ``web_url`` is the address of a web page which is associated with a
    media file and ``media_url`` is the direct URL to the media.

    Behind the scenes, :mod:`urlresolver` will check each of the available
    resolver plugins to see if they accept the ``web_url`` in priority order
    (lowest priotity number first). When it finds a plugin willing to resolve
    the URL, it passes the ``web_url`` to the plugin and returns the direct URL
    to the media file, or ``False`` if it was not possible to resolve.

	.. seealso::

		:class:`HostedMediaFile`

    Args:
        web_url (str): A URL to a web page associated with a piece of media
        content.

    Returns:
        If the ``web_url`` could be resolved, a string containing the direct
        URL to the media file, if not, returns ``False``.
    """
    source = HostedMediaFile(url=web_url)
    return source.resolve()


def filter_source_list(urls):
    """
    Takes a list of :class:`HostedMediaFile`s representing web pages that are
    thought to be associated with media content. If no resolver plugins exist
    to resolve a :class:`HostedMediaFile` to a link to a media file it is
    removed from the list.

    Args:
        urls (list of :class:`HostedMediaFile`): A list of
        :class:`HostedMediaFiles` representing web pages that are thought to be
        associated with media content.

    Returns:
        The same list of :class:`HostedMediaFile` but with any that can't be
        resolved by a resolver plugin removed.

    """
    return [source for source in urls if source]


