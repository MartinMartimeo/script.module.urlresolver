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

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
import urllib2


# Custom imports
import re


class FlashxResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "flashx"

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)

        #e.g. http://flashx.tv/player/embed_player.php?vid=1503&width=600&height=370&autoplay=no
        self.pattern = 'http://((?:www.|play.)?flashx.tv)/(?:player/embed_player.php\?vid=|player/embed.php\?vid=|video/)([0-9A-Z]+)'


    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        try:
            html = http_get(web_url)
        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                   (e.code, web_url))
            return False
            #grab stream url
        sPatternHQ = "var hq_video_file\s*=\s*'([^']+)'"        # .mp4
        #sPatternLQ = "var normal_video_file\s*=\s*'([^']+)'"    # .flv old
        sPatternLQ = "\?hash=([^'|&]+)"
        r = re.search(sPatternLQ, html)
        if r:
            print r.group(1)
            media_id = r.group(1)
            #return r.group(1)
        try:
            html = self.net.http_GET("http://play.flashx.tv/nuevo/player/cst.php?hash=" + media_id).content
        except urllib2.URLError, e:
            common.addon.log_error(self.name + ': got http error %d fetching %s' %
                                   (e.code, web_url))
            return False
        pattern = "<file>(.*?)</file>"
        r = re.search(pattern, html)
        if r:
            return r.group(1)

        return False

    def get_url(self, host, media_id):
        return 'http://www.flashx.tv/player/embed_player.php?vid=%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match(self.pattern, url) or self.name in host
