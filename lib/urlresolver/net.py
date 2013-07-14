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
import requests


def http_head(url):
    """
        HTTP HEAD request

        :param url: URL to be fetched
    """
    return requests.head(url)


def http_get(url, data=None):
    """
        HTTP GET an url

        :param url: URL to be fetched
        :param data: Data to be posted
    """
    if data is not None:
        r = requests.get(url, data=data)
    else:
        r = requests.get(url)
    r.raise_for_status()
    return r.text


def http_request(url, **kwargs):
    """
        HTTP GET request

        :param url: URL to be fetched
    """
    return requests.get(url, **kwargs)


def http_post(url, data, **kwargs):
    """
        HTTP POST an url

        :param url: URL to be fetched
        :param data: Data to be posted
    """
    r = requests.post(url, data=data, **kwargs)
    r.raise_for_status()
    return r.text
