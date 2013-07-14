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
from urlresolver.net import http_get

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2, re, os


class SkyloadResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "skyload"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

        self.pattern = 'http://((?:www.)?skyload.net)/File/([0-9a-zA-Z]+).flv'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = http_get(web_url)

        sPattern = 'var targetURL="([^"]+)"'
        r = re.search(sPattern, html)
        if r:
            return r.group(1)
        else:
            sPattern = "file','([^']+)'"
            r = re.search(sPattern, html)
            if r:
                return r.group(1)
            raise Exception('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://skyload.net/File/%s.flv' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host
