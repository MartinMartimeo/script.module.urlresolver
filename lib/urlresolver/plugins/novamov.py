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

import re, urllib2, os
from urlresolver.net import http_get

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin


class NovamovResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "novamov"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        #find key
        html = http_get(web_url)
        r = re.search('flashvars.file="(.+?)".+?flashvars.filekey="(.+?)"',
                      html, re.DOTALL)
        print 'find key: ' + str(r)
        if r:
            filename, filekey = r.groups()
            print "FILEBLOBS=%s  %s" % (filename, filekey)
        else:
            r = re.search('file no longer exists', html)
            if r:
                raise Exception('File Not Found or removed')


        #get stream url from api
        if 'movshare' in host:
            api = 'http://www.movshare.net/api/player.api.php?key=%s&file=%s' % (filekey, filename)
        elif 'nowvideo' in host:
            api = 'http://www.nowvideo.eu/api/player.api.php?key=%s&file=%s' % (filekey, filename)
        elif 'novamov' in host:
            api = 'http://www.novamov.com/api/player.api.php?key=%s&file=%s' % (filekey, filename)
        print api
        html = self.net.http_GET(api).content
        r = re.search('url=(.+?)&title', html)
        if r:
            stream_url = r.group(1)
        else:
            r = re.search('file no longer exists', html)
            if r:
                raise Exception('File Not Found or removed')

        return stream_url


    def get_url(self, host, media_id):
        if 'movshare' in host:
            return 'http://www.movshare.net/video/%s' % media_id
        elif 'nowvideo' in host:
            return 'http://www.nowvideo.eu/video/%s' % media_id
        elif 'novamov' in host:
            return 'http://www.novamov.com/video/%s' % media_id


    def get_host_and_id(self, url):
        if 'nowvideo' in url:
            r = re.search('http://(www.|embed.nowvideo.eu)/(?:video/|embed.php\?v=([0-9a-z]+)&width)', url)
        if 'movshare' in url:
            r = re.search('//(www.movshare.net)/(?:video|embed)/([0-9a-z]+)', url)
        else:
            r = re.search('//(?:embed.)?(.+?)/(?:video/|embed.php\?v=)' +
                          '([0-9a-z]+)', url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http://(www.|embed.)?no.+?/(video/|embed.php\?)', url) or 'novamov' in host or re.match(
            'http://(?:www.)?movshare.net/(?:video|embed)/', url) or 'movshare' in host or re.match(
            'http://(www.|embed.)?nowvideo.(?:eu)/(video/|embed.php\?)' +
            '(?:[0-9a-z]+|width)', url) or 'nowvideo' in host

