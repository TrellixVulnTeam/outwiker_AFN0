# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import os
import os.path
import re
from io import BytesIO
import urllib.request
import urllib.error
import urllib.parse
import gzip
from typing import Callable

import wx

from .events import UpdateLogEvent

from .i18n import get_


class BaseDownloader(object):
    def __init__(self, timeout):
        self._timeout = timeout
        global _
        _ = get_()

        self._encoding = None

    def download(self, url):
        # if not os.path.isfile(url) and not url.startswith('file:/'):
        #     url = self.fix_url(url)

        opener = urllib.request.build_opener()
        opener.addheaders = [
            ('User-agent', 'Mozilla/5.0(Windows NT 6.1) AppleWebKit/537.36(KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36 OutWiker/1'),
            ('Accept-encoding', 'gzip'),
        ]
        response = opener.open(url, timeout=self._timeout)
        if response.info().get('Content-Encoding') == 'gzip':
            buf = BytesIO(response.read())
            zipfile = gzip.GzipFile(fileobj=buf)
            return zipfile
        return response

    def toUnicode(self, text):
        from bs4 import UnicodeDammit
        dammit = UnicodeDammit(text)
        text = dammit.unicode_markup
        return text

    def fix_url(self, url):
        result = url
        if isinstance(url, str):
            (scheme, netloc, path, query, fragment) = urllib.parse.urlsplit(url)
            scheme = urllib.parse.quote(scheme)
            netloc = netloc.encode('idna').decode('utf8')
            path = urllib.parse.quote(path)

            # Restore '@' symbol after quote
            # For example: https://vk.com/@etorabotaet-10-luchshih-non-fiction-knig-2017-goda
            path = path.replace('%40', '@')
            # query = urllib.parse.quote(query)
            fragment = urllib.parse.quote(fragment)
            result = urllib.parse.urlunsplit(
                (scheme, netloc, path, query, fragment))

        return result


class Downloader(BaseDownloader):
    def __init__(self, timeout=20):
        super().__init__(timeout)

        self._contentSrc = None
        self._pageTitle = None
        self._faviconPath = None

        self._soup = None

        self._contentResult = None
        self._success = False

    def start(self, url, controller):
        from bs4 import BeautifulSoup
        self._success = False

        if not os.path.isfile(url) and not url.startswith('file:/'):
            url = self.fix_url(url)

        obj = self.download(url)
        html = obj.read()

        self._soup = BeautifulSoup(html, "html5lib")
        self._contentSrc = self._soup.prettify()

        if self._soup.title is not None:
            self._pageTitle = self._soup.title.string

        baseUrl = self._getBaseUrl(self._soup, url)

        self._downloadImages(self._soup, controller, baseUrl)
        self._downloadCSS(self._soup, controller, baseUrl)
        self._downloadScripts(self._soup, controller, baseUrl)
        self._downloadFavicon(self._soup, controller, baseUrl)

        self._faviconPath = controller.favicon

        self._improveResult(self._soup, baseUrl)

        self._contentResult = str(self._soup)
        self._success = True

    def _getBaseUrl(self, soup, url):
        result = url
        for basetag in soup.find_all(u'base'):
            if basetag.has_attr(u'href'):
                result = basetag[u'href']
        return result

    def _improveResult(self, soup, url):
        self._removeBaseTag(soup)

    def _removeBaseTag(self, soup):
        for basetag in soup.find_all(u'base'):
            basetag.extract()

    @property
    def success(self):
        return self._success

    def _downloadImageSrc(self, controller, startUrl, image_node):
        if image_node.has_attr(u'src'):
            try:
                controller.processImg(startUrl, image_node['src'], image_node)
            except BaseException as e:
                controller.log(str(e))

    def _downloadImageSrcSet(self, controller, startUrl, image_node):
        if image_node.has_attr(u'srcset'):
            srcset = image_node['srcset']
            srcset_items_processed = []

            for srcset_item in srcset.split(','):
                srcset_item = srcset_item.strip()
                srcset_params = srcset_item.split(' ')
                url = srcset_params[0]

                try:
                    relative_path = controller.processImg(startUrl, url, None)
                    item_processed = ' '.join([relative_path] + srcset_params[1:])
                    srcset_items_processed.append(item_processed)
                except BaseException as e:
                    controller.log(str(e))

            srcset_processed = ', '.join(srcset_items_processed)
            image_node['srcset'] = srcset_processed

    def _downloadImages(self, soup, controller, startUrl):
        images = soup.find_all(u'img')
        for image_node in images:
            self._downloadImageSrc(controller, startUrl, image_node)
            self._downloadImageSrcSet(controller, startUrl, image_node)

    def _downloadCSS(self, soup, controller, startUrl):
        links = soup.find_all(u'link')
        for link in links:
            if(link.has_attr('rel') and
                    link.has_attr('href') and
                    link['rel'][0].lower() == u'stylesheet'):
                try:
                    controller.processCSS(startUrl, link['href'], link)
                except BaseException as e:
                    controller.log(str(e))

    def _downloadScripts(self, soup, controller, startUrl):
        scripts = soup.find_all(u'script')
        for script in scripts:
            if script.has_attr('src'):
                try:
                    controller.processScript(startUrl, script['src'], script)
                except BaseException as e:
                    controller.log(str(e))

    def _downloadFavicon(self, soup, controller, startUrl):
        links = soup.find_all(u'link')
        for link in links:
            if (link.has_attr('rel') and
                    link.has_attr('href') and
                    u'icon' in link['rel']):
                try:
                    controller.processFavicon(startUrl, link['href'], link)
                except BaseException as e:
                    controller.log(str(e))

        if controller.favicon is None:
            try:
                controller.processFavicon(startUrl, u'/favicon.ico', None)
            except BaseException as e:
                controller.log(str(e))

    @property
    def contentSrc(self):
        return self._contentSrc

    @property
    def contentResult(self):
        return self._contentResult

    @property
    def pageTitle(self):
        return self._pageTitle

    @property
    def favicon(self):
        return self._faviconPath


class BaseDownloadController(BaseDownloader, metaclass=ABCMeta):
    '''
    Instance the class select action for every downloaded file
    '''

    def __init__(self, timeout=20):
        super().__init__(timeout)
        self.favicon = None

    @abstractmethod
    def processImg(self, startUrl, url, node):
        pass

    @abstractmethod
    def processCSS(self, startUrl, url, node):
        pass

    @abstractmethod
    def processScript(self, startUrl, url, node):
        pass

    @abstractmethod
    def processFavicon(self, startUrl, url, node):
        """
        startUrl - downloaded page URL.
        url - favicon url.
        node - link node instance if this tag exists or None otherwise.
        """
        pass

    def log(self, text):
        pass


class DownloadController(BaseDownloadController):
    """
    Class with main logic for downloading
    """

    def __init__(self, rootDownloadDir, staticDir, timeout=20):
        super().__init__(timeout)

        self._rootDownloadDir = rootDownloadDir
        self._staticDir = staticDir
        self._fullStaticDir = os.path.join(rootDownloadDir,
                                           staticDir).replace(u'\\', u'/')

        # Key - url from source HTML page,
        # value - relative path to downloaded file
        self._staticFiles = {}

    def processImg(self, startUrl, url, node):
        if not(url.startswith(u'data:') or url.startswith(u'mhtml:')):
            relative_path = self._process(startUrl, url, node, self._processFuncNone)

            if node is not None and node.name == 'img':
                node['src'] = relative_path

            return relative_path

    def processCSS(self, startUrl, url, node):
        self.log(_(u'Processing: {}\n').format(url))
        relative_path = self._process(startUrl, url, node, self._processFuncCSS)

        if node is not None and node.name == 'link':
            node['href'] = relative_path

        return relative_path

    def processScript(self, startUrl, url, node):
        relative_path = self._process(startUrl, url, node, self._processFuncNone)

        if node is not None and node.name == 'script':
            node['src'] = relative_path

        return relative_path

    def processFavicon(self, startUrl, url, node):
        """
        startUrl - downloaded page URL.
        url - favicon url.
        node - link node instance if this tag exists or None otherwise.
        """
        if self.favicon is None:
            relativeDownloadPath = self._process(startUrl,
                                                 url,
                                                 node,
                                                 self._processFuncNone)
            fullDownloadPath = os.path.join(self._rootDownloadDir,
                                            relativeDownloadPath)
            if os.path.exists(fullDownloadPath):
                self.favicon = fullDownloadPath

    def _processFuncNone(self, startUrl, url, node, text):
        return text

    def _processFuncCSS(self, startUrl, url, node, text):
        text = self.toUnicode(text)
        regexp_url = re.compile(r'''url\((?P<url>.*?)\)''',
                                re.X | re.U | re.I)
        repace_tpl_url = u'url("{url}")'

        regexp_import = re.compile(r'''@import\s+
                                   (?P<quote>['"])
                                   (?P<url>.*?)
                                   (?P=quote)''',
                                   re.X | re.U | re.I)
        replace_tmpl_import = u'@import "{url}"'

        text = self._processCSSContent(startUrl,
                                       url,
                                       text,
                                       regexp_url,
                                       repace_tpl_url)
        text = self._processCSSContent(startUrl,
                                       url,
                                       text,
                                       regexp_import,
                                       replace_tmpl_import)
        return text

    def _processCSSContent(self, startUrl, url, text, regexp, replace_tpl):
        delta = 0

        result = text

        for match in regexp.finditer(text):
            url_found = match.group('url')
            url_found = url_found.strip()
            url_found = url_found.replace(u'"', u'')
            url_found = url_found.replace(u"'", u'')

            if (url_found.startswith(u'data:') or
                    url_found.startswith(u'mhtml:')):
                continue
            elif url_found.startswith(u'/') or u'://' in url_found:
                relativeurl = url_found
            else:
                relativeurl = os.path.join(os.path.dirname(url), url_found)
                relativeurl = relativeurl.replace(u'\\', u'/')

            processFunc = (self._processFuncCSS
                           if url_found.endswith(u'.css')
                           else self._processFuncNone)

            relativeDownloadPath = self._process(startUrl,
                                                 relativeurl,
                                                 None,
                                                 processFunc)
            replace = replace_tpl.format(
                url=relativeDownloadPath.replace(self._staticDir + u'/',
                                                 u'',
                                                 1)
            )

            result = result[:match.start() + delta] + replace + \
                result[match.end() + delta:]
            delta += len(replace) - (match.end() - match.start())

        return result

    def urljoin(self, startUrl, url):
        if u'://' in url:
            return url

        return urllib.parse.urljoin(startUrl, url)

    def _process(self,
            startUrl: str,
            url: str,
            node: 'bs4.element.Tag',
            processFunc: Callable[[str, str, 'bs4.element.Tag', bytes], str]) -> str:
        # Create a directory for downloaded files
        if not os.path.exists(self._fullStaticDir):
            os.mkdir(self._fullStaticDir)

        fullUrl = self.urljoin(startUrl, url)

        relativeDownloadPath = self._getRelativeDownloadPath(fullUrl)
        fullDownloadPath = os.path.join(self._rootDownloadDir,
                                        relativeDownloadPath)

        if fullUrl not in self._staticFiles:
            self.log(_(u'Download: {}\n').format(fullUrl))
            try:
                obj = self.download(fullUrl)
                with open(fullDownloadPath, 'wb') as fp:
                    data = obj.read()
                    text = processFunc(startUrl, url, node, data)
                    if isinstance(text, str):
                        fp.write(text.encode(u'utf8'))
                    else:
                        fp.write(text)
            except(urllib.error.URLError, IOError):
                self.log(_(u"Can't download {}\n").format(url))

            self._staticFiles[fullUrl] = relativeDownloadPath

        return relativeDownloadPath

    def _getRelativeDownloadPath(self, url):
        """
        Return relative path to download.
        For example: '__download/image.png'
        """
        if url in self._staticFiles:
            return self._staticFiles[url]

        path = urllib.parse.urlparse(url).path
        if path.endswith(u'/'):
            path = path[:-1]

        slashpos = path.rfind('/')
        if slashpos != -1:
            fname = path[slashpos + 1:]
        else:
            fname = path

        relativeDownloadPath = u'{}/{}'.format(self._staticDir, fname)
        result = relativeDownloadPath

        fullDownloadPath = os.path.join(self._rootDownloadDir,
                                        result)

        number = 1
        while os.path.exists(fullDownloadPath):
            dotpos = relativeDownloadPath.rfind(u'.')
            if dotpos == -1:
                newRelativePath = u'{}_{}'.format(relativeDownloadPath, number)
            else:
                newRelativePath = u'{}_{}{}'.format(
                    relativeDownloadPath[:dotpos],
                    number,
                    relativeDownloadPath[dotpos:]
                )

            result = newRelativePath
            fullDownloadPath = os.path.join(self._rootDownloadDir,
                                            newRelativePath)
            number += 1

        return result


class WebPageDownloadController(DownloadController):
    """
    DownloadController for using for creation WebPage.
    Downloading can be terminated with event.
    Log will be send with UpdateLogEvent
    """

    def __init__(self, runEvent, rootDownloadDir, staticDir, dialog, timeout=20):
        super().__init__(rootDownloadDir,
                         staticDir,
                         timeout)
        self._runEvent = runEvent
        self._dialog = dialog

    def processImg(self, startUrl, url, node):
        if self._runEvent.is_set():
            return super().processImg(startUrl, url, node)

    def processCSS(self, startUrl, url, node):
        if self._runEvent.is_set():
            return super().processCSS(startUrl, url, node)

    def processScript(self, startUrl, url, node):
        if self._runEvent.is_set():
            return super().processScript(startUrl, url, node)

    def processFavicon(self, startUrl, url, node):
        if self._runEvent.is_set():
            return super().processFavicon(startUrl, url, node)

    def log(self, text):
        event = UpdateLogEvent(text=text)
        wx.PostEvent(self._dialog, event)
