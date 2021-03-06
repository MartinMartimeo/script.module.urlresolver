"""
Vidbull urlresolver plugin
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
import re, urllib2, os

from lib import jsunpack


class VidbullResolver(Plugin, UrlResolver, PluginSettings):
    """
        Resolves Vidbull
    """
    implements = [UrlResolver, PluginSettings]
    name = "vidbull"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)


    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        html = http_get(url)
        check = re.compile(r'File Not Found').findall(html)
        if check:
            raise Exception('File Not Found or removed')

        data = {}
        r = re.findall(r'type="hidden" name="((?!(?:.+premium)).+?)"\s* value="?(.+?)">', html)
        for name, value in r:
            data[name] = value

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
            raise Exception('File Not Found or removed')

        else:
            num = re.compile('event\|(.+?)\|aboutlink').findall(html)
            pre = 'http://' + num[0] + '.vidbull.com:182/d/'
            preb = re.compile('image\|(.+?)\|video\|(.+?)\|').findall(html)
            for ext, link in preb:
                r = pre + link + '/video.' + ext
                return r
        return False

    def get_url(self, host, media_id):
        return 'http://www.vidbull.com/%s' % media_id


    def get_host_and_id(self, url):
        r = re.search('//(.+?)/(?:embed-)?([0-9a-zA-Z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return (re.match('http://(www.)?vidbull.com/' +
                         '[0-9A-Za-z]+', url) or
                'vidbull' in host)
