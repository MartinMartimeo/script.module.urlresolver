"""
    urlresolver XBMC Addon
    Copyright (C) 2012 Bstrdsmkr

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
import urllib2, re, os

from lib import jsunpack


class ZalaaResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "zalaa"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

        #e.g.  http://www.zalaa.com/hj0eyq4jg0io
        #FIXME: http://www.zalaa.com/npwp1cr4uys7/Nikita.S02E14.HDTV.XviD-LOL.avi.htm
        self.pattern = 'http://www.(zalaa.com)/([a-zA-Z0-9]+)(?:/.+?\.htm)?'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = http_get(web_url)
        r = 'method="POST"\s+name=\'frmdownload\'.+?"ipcount_val" value="'
        r += '([0-9]+)".+?"op"\s+value="(.+?)".+?name="fname"\s+value="(.+?)"'

        r = re.search(r, html, re.DOTALL)
        ipcount_val, op, fname = r.groups()
        data = {'ipcount_val': ipcount_val}
        data['op'] = op
        data['usr_login'] = ''
        data['id'] = media_id
        data['fname'] = fname
        data['referer'] = web_url
        data['method_free'] = 'Slow access'

        html = self.net.http_POST(web_url, data).content
        # get url from packed javascript
        sPattern = '<script type=(?:"|\')text/javascript(?:"|\')>(eval\('
        sPattern += 'function\(p,a,c,k,e,d\)(?!.+player_ads.+).+np_vid.+?)'
        sPattern += '\s+?</script>'
        r = re.search(sPattern, html, re.DOTALL + re.IGNORECASE)
        if r:
            sJavascript = r.group(1)
            sUnpacked = jsunpack.unpack(sJavascript)
            print(sUnpacked)
            sPattern = '<embed id="np_vid"type="video/divx"src="(.+?)'
            sPattern += '"custommode='
            r = re.search(sPattern, sUnpacked)
            if r:
                return r.group(1)

        raise Exception('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.zalaa.com/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False


    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host
