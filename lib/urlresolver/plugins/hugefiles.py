"""
Hugefiles urlresolver plugin
Copyright (C) 2013 Vinnydude

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from urlresolver.net import http_get, http_post

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re, xbmcgui, os, urllib2

from lib import jsunpack


class HugefilesResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "hugefiles"


    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        html = http_get(url)
        r = re.findall('File Not Found', html)
        if r:
            raise Exception('File Not Found or removed')
        dialog = xbmcgui.DialogProgress()
        dialog.create('Resolving', 'Resolving Hugefiles Link...')
        dialog.update(0)

        data = {}
        r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', html)
        for name, value in r:
            data[name] = value
            data.update({'method_free': 'Free Download'})
        html = http_post(url, data)

        dialog.update(50)

        sPattern = """<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>"""
        r = re.findall(sPattern, html, re.DOTALL | re.I)
        if r:
            sUnpacked = jsunpack.unpack(r[0])
            sUnpacked = sUnpacked.replace("\\'", "")
            r = re.findall('file,(.+?)\)\;s1', sUnpacked)
            if not r:
                r = re.findall('"src"value="(.+?)"/><embed', sUnpacked)
            dialog.update(100)
            dialog.close()
            return r[0]
        if not r:
            return self.unresolvable()

    def get_url(self, host, media_id):
        return 'http://hugefiles.net/%s' % media_id


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)', url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?hugefiles.net/' +
                         '[0-9A-Za-z]+', url) or
                'hugefiles' in host)
