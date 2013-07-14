'''
2gbhosting urlresolver plugin
Copyright (C) 2011 t0mm0, DragonWin, jas0npc

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
'''
from urlresolver import log_debug
from urlresolver.net import http_get, http_post

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from lib import jsunpack
import re, urllib2, os


class TwogbhostingResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "2gbhosting"


    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = http_get(web_url)
        r = re.search('<input type="hidden" name="k" value="(.+?)" />', html)
        if not r:
            raise Exception('File Not Found or removed')
        if r:
            sid = r.group(1)
            log_debug('eg-hosting: found k' + sid)
            data = {'k': sid, 'submit': 'Click Here To Continue', }
            html = http_post(web_url, data)
            r = re.findall("text/javascript'>\n.+?(eval\(function\(p,a,c,k,e,d\).+?)\n.+?</script>", html, re.I | re.M)
            if r:
                unpacked = jsunpack.unpack(r[0])
                unpacked = str(unpacked).replace('\\', '')
                r = re.findall(r"file\':\'(.+?)\'", unpacked)
                return r[0]
            if not r:
                raise Exception('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.2gb-hosting.com/videos/%s' % media_id + '.html'


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/[videos|v]/([0-9a-zA-Z/]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?2gb-hosting.com/[videos|v]/' +
                         '[0-9A-Za-z]+/[0-9a-zA-Z]+.*', url) or
                '2gb-hosting' in host)
