"""
    nolimitvideo urlresolver plugin
    Copyright (C) 2011 t0mm0, DragonWin

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
import re, os, urllib2


class nolimitvideoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "nolimitvideo"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = http_get(web_url)
        r = re.search('\'file\': \'(.+?)\',', html)
        stream_url = ""
        if r:
            stream_url = r.group(1)
        else:
            raise Exception('File Not Found or removed')

        return stream_url


    def get_url(self, host, media_id):
        return 'http://www.nolimitvideo.com/video/%s' % media_id


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/video/([0-9a-f]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http://(www)?.nolimitvideo.com/video/[0-9a-f]+/',
                        url) or 'nolimitvideo' in host

