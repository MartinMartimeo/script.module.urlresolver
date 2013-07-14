"""
Cyberlocker urlresolver plugin
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
from urlresolver.net import http_post, http_get

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import re

from lib import jsunpack


class CyberlockerResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "cyberlocker"


    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)


    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        html = http_get(url)
        r = re.findall('<center><h3>File Not Found</h3></center><br>', html, re.I)
        if r:
            raise Exception('File Not Found or removed')
        data = {}
        r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', html)
        for name, value in r:
            data[name] = value
            data['method_free'] = 'Wait for 0 seconds'

        html = http_post(url, data)

        sPattern = '<script type=(?:"|\')text/javascript(?:"|\')>(eval\('
        sPattern += 'function\(p,a,c,k,e,d\)(?!.+player_ads.+).+np_vid.+?)'
        sPattern += '\s+?</script>'
        r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)
        if r:
            sJavascript = r.group(1)
            sUnpacked = jsunpack.unpack(sJavascript)
            sPattern = '<embed id="np_vid"type="video/divx"src="(.+?)'
            sPattern += '"custommode='
            r = re.search(sPattern, sUnpacked)
            if r:
                return r.group(1)

        else:
            num = re.compile('cyberlocker\|(.+?)\|http').findall(html)
            pre = 'http://' + num[0] + '.cyberlocker.ch:182/d/'
            preb = re.compile('image\|(.+?)\|video\|(.+?)\|').findall(html)
            for ext, link in preb:
                r = pre + link + '/video.' + ext
                return r

    def get_url(self, host, media_id):
        return 'http://cyberlocker.ch/%s' % media_id


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/([0-9a-zA-Z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?cyberlocker.ch/' +
                         '[0-9A-Za-z]+', url) or
                'cyberlocker' in host)
