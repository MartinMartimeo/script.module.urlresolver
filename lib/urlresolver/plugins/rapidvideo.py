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
import urllib2

# Custom imports
import re


class RapidvideoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "rapidvideo"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        #e.g. http://rapidvideo.com/view/hwksai28
        self.pattern = 'http://((?:www.)?rapidvideo.com)/view/([0-9a-zA-Z]+)'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = http_get(web_url)

        # get stream url
        sPattern = "so.addVariable\(\s*'file'\s*,\s*'([^']+)'\s*\)"
        r = re.search(sPattern, html)
        if r:
            return r.group(1)

        return False

    def get_url(self, host, media_id):
            return 'http://rapidvideo.com/view/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host