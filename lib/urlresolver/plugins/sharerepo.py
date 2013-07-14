"""
Sharerepo urlresolver plugin
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
import re

from lib import jsunpack


class SharerepoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "sharerepo"


    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)


    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        html = http_get(url)
        data = {}
        r = re.findall(r'type="(?:hidden|submit)?" name="(.+?)"\s* value="?(.+?)">', html)
        for name, value in r:
            data[name] = value

        html = http_post(url, data)

        sPattern = """<div id="player_code">.*?<script type='text/javascript'>(eval.+?)</script>"""
        r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)

        if r:
            sJavascript = r.group(1)
            sUnpacked = jsunpack.unpack(sJavascript)
            sPattern = """("video/divx"src="|addVariable\('file',')(.+?)video[.]"""
            r = re.search(sPattern, sUnpacked)
            if r:
                link = r.group(2)
                return link
            raise Exception('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://sharerepo.com/%s' % media_id


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?sharerepo.com/' +
                         '[0-9A-Za-z]+', url) or
                'sharerepo' in host)
