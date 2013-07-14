#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
#    urlresolver XBMC Addon
#    Copyright (C) 2011 t0mm0
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
This module defines several interfaces that you can implement when writing 
your URL resolving plugin.

* :class:`UrlResolver`: Resolves URLs. All plugins should implement this.
* :class:`SiteAuth`: Handles logging in to the file hoster.
* :class:`PluginSettings`: Allows a plugin to save and retrieve settings.

Interfaces you wish to implement must be included in the inheritance list of
you class definition, as well as added to the ``implements`` attribute of your
class.

For example, if you want to implement all the available interfaces, your plugin 
should be defined as follows::

        class MyPluginResolver(Plugin, UrlResolver, SiteAuth, PluginSettings):
            implements = [UrlResolver, SiteAuth, PluginSettings]

"""
from abc import abstractmethod

from urlresolver import get_setting
from urlresolver.plugnplay import Interface


class UrlResolver(Interface):
    """
    Your plugin needs to implement the abstract methods in this interface if
    it wants to be able to resolve URLs (which is probably all plugins!)

    .. note::

        You **MUST** override :meth:`get_media_url` and :meth:`valid_url` as
        well as :attr:`name`.

    There are also a couple of utlity methods which you should probably not
    override.
    """

    # (str) A human readable name for your plugin.
    name = 'override_me'

    # (int) The order in which plugins will be tried. Lower numbers are tried first.
    priority = 100

    class unresolvable(object):
        """
        An object returned to indicate that the url could not be resolved
        
        This object always evaluates to False to maintain compatibility with
        legacy implementations.
        
        Args:
            code (int): Identifies the general reason a url could not be
            resolved from the following list:
                0: Unknown Error
                1: The url was resolved, but the file has been permanantly
                    removed
                2: The file is temporarily unavailable for example due to
                    planned site maintenance
                3. There was an error contacting the site for example a
                    connection attempt timed out

            msg (str): A string (likely shown to the user) with more
            detailed information about why the url could not be resolved
        """

        def __init__(self, code=0, msg='Unknown Error'):
            self.code = code
            self.msg = msg

        def __nonzero__(self):
            return 0

    @abstractmethod
    def get_media_url(self, host, media_id):
        """
        The part of your plugin that does the actual resolving. You must 
        implement this method.
        
        Ths method will be passed the URL of a web page associated with a media
        file. It will only get called if your plugin's :meth:`valid_url` method
        has returned ``True`` so it will definitely be a URL for the file host
        (or hosts) your plugin is capable of resolving (assuming you implemented
        :meth:`valid_url` correctly!)
        
        The URL you return must be something that is playable by XBMC.
        
        If for any reason you cannot resolve the URL (eg. the file has been 
        removed) then return ``False`` instead.
        
        Args:
            host (str): Host of this piece of media
            media_id (str): media_id of this piece of media
            
        Returns:
            If the ``web_url`` could be resolved, a string containing the direct 
            URL to the media file, if not, returns ``False``.    
        """
        raise NotImplementedError("Unimplemented abstract method")

    def get_url(self, host, media_id):
        """
            Resolve host/media_id to url
        """
        raise NotImplementedError("Unimplemented abstract method")

    def get_host_and_id(self, url):
        """
            Resolve url to host/media_id
        """
        raise NotImplementedError("Unimplemented abstract method")

    def valid_url(self, host, media_id):
        """
        Determine whether this plugin is capable of resolving this URL. You must 
        implement this method.
        
        The usual way of implementing this will be using a regular expression
        which returns ``True`` if the URL matches the pattern (or patterns)
        used by the file host your plugin can resolve URLs for. 

        Args:
            host (str): Host of this piece of media
            media_id (str): media_id of this piece of media
            
        Returns:
            ``True`` if this plugin thinks it can resolve the ``web_url``, 
            otherwise ``False``.
        """
        raise NotImplementedError("Unimplemented abstract method")

    def get_media_urls(self, web_urls):
        """
        .. warning::

            Do not override this method!

        Calls :meth:`get_media_url` on each URL in a list. May not be very
        useful!

        Args:
            web_urls (str): A list of URLs to web pages associated with media
            content.

        Returns:
            A list of results - if the ``web_url`` could be resolved, a string
            containing the direct URL to the media file, if not, returns
            ``False``.
        """
        ret_val = []
        for web_url in web_urls:
            if isinstance(web_url, str):
                url = self.get_media_url(*self.get_host_and_id(web_url))
            elif isinstance(web_url, tuple):
                url = self.get_media_url(*web_url)
            elif isinstance(web_url, object):
                url = self.get_media_url(web_url.get_host(), web_url.get_media_id())
            else:
                continue
            if url:
                ret_val.append(url)
        return ret_val

    def filter_urls(self, web_urls):
        """
        .. warning::
        
            Do not override this method!
            
        Calls :meth:`get_media_url` on each URL in a list. May not be very
        useful!
        
        Args:
            web_urls (str): A list of URLs to web pages associated with media
            content.
            
        Returns:
            A list of results - ``True`` if this plugin thinks it can resolve 
            the ``web_url``, otherwise ``False``.
        """
        ret_val = []
        for web_url in web_urls:
            if isinstance(web_url, str):
                valid = self.get_media_url(*self.get_host_and_id(web_url))
            elif isinstance(web_url, tuple):
                valid = self.get_media_url(*web_url)
            elif isinstance(web_url, object):
                valid = self.get_media_url(web_url.get_host(), web_url.get_media_id())
            else:
                continue
            if valid:
                ret_val.append(web_url)
        return

    def isUniversal(self):
        """
            You need to override this to return True, if you are implementing a univeral resolver
            like real-debrid etc., which handles multiple hosts
        """
        return False


class SiteAuth(Interface):
    """
    Your plugin should implement this interface if the file hoster you are
    resolving URLs for requires authentication. You may also implement it if
    the file hoster supports authentication but doesn't require it.
    """

    def login(self):
        """
        This method should perform the login to the file host site. This will
        normally involve posting credentials (stored in your plugin's settings)
        to a web page which will set cookies.
        """
        raise NotImplementedError("Unimplemented abstract method")


class PluginSettings(Interface):
    """
    Your plugin needs to implement this interface if your plugin needs to store
    settings. 
    
    Plugin settings are global. This means that the user only needs to set your 
    plugin settings (such as username and password) once and they will be 
    available when your plugin is called from any XBMC addon.
    
    Addons can display all :mod:`urlresolver` settings including those of all
    available plugins by calling :func:`urlresolver.show_settings`.
    
    If you only want a 'priority' setting for your plugin, all you need to do
    is add this interface to he classes your plugin inherits from and to the 
    ``implements`` attribute without overriding anything.
    
    To do this your class should begin::
    
        class MyPluginResolver(Plugin, UrlResolver, PluginSettings):
            implements = [UrlResolver, PluginSettings]
            name = "myplugin"

    If you want custom settings you mut override :meth:`get_settings_xml`.
    
    You should never override :meth:`get_setting`.
    """

    def get_settings_xml(self):
        """
        This method should return XML which describes the settings you would 
        like for your plugin. You should make sure that the ``id`` starts
        with your plugins class name (which can be found using 
        :attr:`self.__class__.__name__`) followed by an underscore.
        
        For example, the following is the code included in the default 
        implementation and adds a priority setting::
        
            xml = '<setting id="%s_priority" ' % self.__class__.__name__
            xml += 'type="number" label="Priority" default="100"/>\\n'
            return xml 
            
        Although of course you know the name of your plugin(!) so you can just 
        write::
        
            xml = '<setting id="MyPlugin_priority" '
            xml += 'type="number" label="Priority" default="100"/>\\n'
            return xml 

        The settings category will be your plugin's :attr:`UrlResolver.name`.
        
        I would link to some documentation of ``resources/settings.xml`` but
        I can't find any. Suggestions welcome!
        
        Override this method if you want your plugin to have more settings than
        just 'priority'. If you do and still want the priority setting you 
        should include the priority code as above in your method.
        
        Returns:
            A string containing XML which would be valid in 
            ``resources/settings.xml``
        """
        xml = '<setting id="%s_priority" ' % self.__class__.__name__
        xml += 'type="number" label="Priority" default="100"/>\n'

        xml += '<setting id="%s_enabled" ' % self.__class__.__name__
        xml += 'type="bool" label="Enabled" default="true"/>\n'
        return xml


    def get_setting(self, key):
        """
        .. warning::
        
            Do not override this method!
            
        Gets a setting that you have previously defined by overriding the 
        :meth:`get_settings_xml` method.
        
        When requesting a setting using this method, you should not include
        the ``MyPlugin_`` prefix of the setting id you defined in 
        :meth:`get_settings_xml`.
        
        For example, if you defined a setting with an id of 
        ``MyPlugin_username``, you would get the setting from your plugin 
        using::
        
            self.get_setting('username')
            
        Args:
            key (str): The name of the setting to retrieve (without the prefix).
            
        Returns:
            A string containing the value stored for the requested setting.
        """
        value = get_setting('%s_%s' %
                            (self.__class__.__name__, key))
        return value
