"""
urlresolver XBMC Addon
Copyright (C) 2011 t0mm0

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
from urlresolver import log_error
from urlresolver.net import http_post, http_get

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2

# Custom imports
import re


class EcostreamResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "ecostream"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.pattern = 'http://((?:www.)?ecostream.tv)/(?:stream|embed)?/([0-9a-zA-Z]+).html'


    def get_media_url(self, host, media_id):
        # emulate click on button "Start Stream" (ss=1)
        web_url = self.get_url(host, media_id) + "?ss=1"
        html = http_post(web_url, {'ss': '1'})

        # get vars
        sPattern = "var t=setTimeout\(\"lc\('([^']+)','([^']+)','([^']+)','([^']+)'\)"
        r = re.findall(sPattern, html)
        if r:
            for aEntry in r:
                sS = str(aEntry[0])
                sK = str(aEntry[1])
                sT = str(aEntry[2])
                sKey = str(aEntry[3])
                # get name of php file
                html = http_get('http://www.ecostream.tv/assets/js/common.js')
                sPattern = "url: '([^=]+)="
                r = re.search(sPattern, html)
                if r is None:
                    log_error(self.name + ': name of php file not found')
                    return False
                    # send vars and retrieve stream url
                sNextUrl = r.group(1) + '=' + sS + '&k=' + sK + '&t=' + sT + '&key=' + sKey
                postParams = ({'s': sS, 'k': sK, 't': sT, 'key': sKey})
                postHeader = ({'Referer': 'http://www.ecostream.tv', 'X-Requested-With': 'XMLHttpRequest'})
                html = http_post(sNextUrl, postParams, headers=postHeader)

                sPattern = '<param name="flashvars" value="file=(.*?)&'
                r = re.search(sPattern, html)
                if r:
                    sLinkToFile = 'http://www.ecostream.tv' + r.group(1)
                    return sLinkToFile

        return False


    def get_url(self, host, media_id):
        return 'http://www.ecostream.tv/stream/%s.html' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url.replace('embed', 'stream'))
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host