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
from urlresolver.net import http_request, http_post

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2, re, os


class VidstreamResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "vidstream"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

        #e.g. http://vidstream.in/xdfaay6ccwqj
        self.pattern = 'http://((?:www.)?vidstream.in)/(.*)'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = http_request(web_url)

        html = resp.text
        post_url = resp.url

        # get post vars
        form_values = {}
        for i in re.finditer('<input.*?name="(.*?)".*?value="(.*?)">', html):
            form_values[i.group(1)] = i.group(2)
        html = http_post(post_url, data=form_values)

        # get stream url
        pattern = 'file:\s*"([^"]+)",'
        r = re.search(pattern, html)
        if r:
            return r.group(1)

        raise Exception('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://vidstream.in/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host
