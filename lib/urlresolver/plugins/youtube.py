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

import re, sys,os
from t0mm0.common.net import Net
import urllib2
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

bromix_path = os.path.dirname(os.path.realpath(__file__)) + "/../../../../plugin.video.youtube/"
sys.path.append(bromix_path)

from resources.lib import youtube
from resources.lib.kodion.impl import Context
from resources.lib.kodion.impl.xbmc import xbmc_items
from resources.lib.youtube.helper import yt_play

__provider__ = youtube.Provider()

class YoutubeResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "Youtube"
    domains = [ 'youtube.com', 'youtu.be' ]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.video_item = None

    def get_media_url(self, host, media_id):
        #just call youtube addon
        params = {'video_id':media_id}
        __context__ = Context(path='/play/', params=params, override=False, plugin_id='plugin.video.youtube', plugin_name="Youtube")
        _video_item = yt_play.play_video(__provider__, __context__, "play")
        if _video_item is None: return self.unresolvable(code=0,msg="WTF")
        self.video_item = xbmc_items.to_video_item(__context__, _video_item)
        del __context__
        return _video_item.get_uri()

    def get_url(self, host, media_id):
        return 'http://youtube.com/watch?v=%s' % media_id

    def get_host_and_id(self, url):
        if url.find('?') > -1:
            queries = common.addon.parse_query(url.split('?')[1])
            video_id = queries.get('v', None) or queries.get('video_id', None) or queries.get('videoid', None)
        else:
            r = re.findall('/([0-9A-Za-z_\-]+)', url)
            if r:
                video_id = r[-1]
        if video_id:
            return ('youtube.com', video_id)
        else:
            common.addon.log_error('youtube: video id not found')
            return self.unresolvable(code=0, msg="youtube: video id not found")

    def get_list_item(self, web_url, host, media_id):
        return self.video_item

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http[s]*://(((www.|m.)?youtube.+?(v|embed)(=|/))|' +
                        'youtu.be/)[0-9A-Za-z_\-]+', 
                        url) or re.match('plugin://plugin.video.youtube/.*play.*video') or (
                        'youtube' in host or 'youtu.be' in host)

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting label="This plugin calls the youtube addon - '
        xml += 'change settings there." type="lsep" />\n'
        return xml
