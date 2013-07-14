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
from urlresolver.net import http_post

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2, os, re


class DaclipsResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "daclips"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

        #e.g. http://daclips.com/vb80o1esx2eb
        self.pattern = 'http://((?:www.)?daclips.(?:in|com))/([0-9a-zA-Z]+)'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        """ Human Verification """
        resp = http_request(web_url)
        html = resp.text
        r = re.findall(r'<span class="t" id="head_title">404 - File Not Found</span>', html)
        if r:
            raise Exception('File Not Found or removed')
        post_url = resp.get_url()
        form_values = {}
        for i in re.finditer('<input type="hidden" name="(.+?)" value="(.+?)">', html):
            form_values[i.group(1)] = i.group(2)
        html = http_post(post_url, data=form_values)
        r = re.search('file:"(.+?)"', html)
        if r:
            return r.group(1) + '.flv'
        if not r:
            raise Exception('File Not Found or removed')


    def get_url(self, host, media_id):
        #return 'http://(daclips|daclips).(in|com)/%s' % (media_id)
        return 'http://daclips.in/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host
