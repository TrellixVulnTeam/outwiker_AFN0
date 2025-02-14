# -*- coding: utf-8 -*-

from threading import Event, Thread
from tempfile import mkdtemp
import urllib.error
import os.path
from shutil import rmtree

import wx

from outwiker.core.tagslist import TagsList
from outwiker.gui.testeddialog import TestedDialog
from outwiker.gui.tagsselector import TagsSelector
from outwiker.core.commands import MessageBox
from outwiker.core.iconmaker import IconMaker
from outwiker.core.commands import getClipboardText
from outwiker.gui.testeddialog import TestedFileDialog

import webpage.events
from webpage.downloader import Downloader, WebPageDownloadController
from webpage.webnotepage import STATIC_DIR_NAME, WebPageFactory
from webpage.utils import isLink

from webpage.i18n import get_


class DownloadDialog(TestedDialog):
    def __init__(self, parent):
        super(DownloadDialog, self).__init__(parent)
        global _
        _ = get_()

        self._createGui()
        self.urlText.SetFocus()

    def _createGui(self):
        mainSizer = wx.FlexGridSizer(cols=1)
        mainSizer.AddGrowableCol(0)
        mainSizer.AddGrowableRow(1)
        mainSizer.AddGrowableRow(2)

        self._addUrlGui(mainSizer)
        self._addTagsList(mainSizer)
        self._addLogGui(mainSizer)
        self._addOkCancel(mainSizer)

        self.SetSizer(mainSizer)
        self.SetTitle(_('Download web page'))
        self.SetMinSize((500, 350))
        self.Fit()

    def _addUrlGui(self, mainSizer):
        urlSizer = wx.FlexGridSizer(cols=3)
        urlSizer.AddGrowableCol(1)

        urlLabel = wx.StaticText(self, label=_('URL or local file'))
        self.urlText = wx.TextCtrl(self)
        self.selectFileButton = wx.Button(self, label=_('...'))
        self.selectFileButton.SetMinSize((30, -1))

        urlSizer.Add(urlLabel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=4)
        urlSizer.Add(self.urlText, 0, wx.ALL | wx.EXPAND, border=2)
        urlSizer.Add(self.selectFileButton,
                     0,
                     wx.ALL | wx.ALIGN_RIGHT,
                     border=2)

        mainSizer.Add(urlSizer, 0, wx.ALL | wx.EXPAND, border=2)

    def _addTagsList(self, mainSizer):
        self.tagsSelector = TagsSelector(self)
        mainSizer.Add(self.tagsSelector, 0, wx.EXPAND, 0)

    def _addLogGui(self, mainSizer):
        self.logText = wx.TextCtrl(self,
                                   style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.logText.SetMinSize((-1, 100))
        mainSizer.Add(self.logText, 0, wx.EXPAND, 0)

    def _addOkCancel(self, mainSizer):
        buttonsSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        mainSizer.Add(buttonsSizer,
                      0,
                      wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL,
                      border=4)

    def setTagsList(self, tagslist):
        self.tagsSelector.setTagsList(tagslist)

    @property
    def url(self):
        return self.urlText.Value.strip()

    @url.setter
    def url(self, url):
        self.urlText.Value = url

    @property
    def tags(self):
        return self.tagsSelector.tags

    @tags.setter
    def tags(self, tags):
        self.tagsSelector.tags = tags


class DownloadDialogController(object):
    def __init__(self, dialog, application, parentPage):
        self._dialog = dialog
        self._application = application
        self._parentPage = parentPage

        global _
        _ = get_()

        self._downloadDir = None

        self._runEvent = Event()
        self._thread = None

        self._logIndex = 1

        self._dialog.Bind(wx.EVT_BUTTON, self._onOk, id=wx.ID_OK)
        self._dialog.Bind(wx.EVT_BUTTON, self._onCancel, id=wx.ID_CANCEL)
        self._dialog.selectFileButton.Bind(wx.EVT_BUTTON, self._onSelectFile)

        self._dialog.Bind(webpage.events.EVT_UPDATE_LOG, self._onLogUpdate)

        self._dialog.Bind(webpage.events.EVT_DOWNLOAD_ERROR,
                          self._onDownloadError)

        self._dialog.Bind(webpage.events.EVT_DOWNLOAD_FINISH,
                          self._onDownloadFinish)

    def showDialog(self):
        """
        The method show the dialog and return result of the ShowModal() method
        """
        if self._application.wikiroot is None:
            return

        self._loadState()

        result = self._dialog.ShowModal()
        if result == wx.ID_OK:
            self._saveState()

        return result

    def addToLog(self, text):
        logString = '[{index:03g}] {text}'.format(index=self._logIndex,
                                                   text=text)
        self._logIndex += 1

        self._dialog.logText.AppendText(logString)

        count = self._dialog.logText.GetLastPosition()
        self._dialog.logText.ShowPosition(count)

    def resetLog(self):
        self._logIndex = 1
        self._dialog.logText.Value = ''

    def _loadState(self):
        tagslist = TagsList(self._application.wikiroot)
        self._dialog.setTagsList(tagslist)
        if (self._parentPage is not None and
                self._parentPage.parent is not None):
            self._dialog.tags = self._parentPage.tags

        clipboardText = getClipboardText()
        if clipboardText is not None and isLink(clipboardText):
            self._dialog.url = clipboardText
            self._dialog.urlText.SetSelection(0, len(clipboardText))

    def _saveState(self):
        pass

    def _onLogUpdate(self, event):
        self.addToLog(event.text)

    def _removeDownloadDir(self):
        if self._downloadDir is not None and os.path.exists(self._downloadDir):
            try:
                rmtree(self._downloadDir)
            except EnvironmentError:
                self.addToLog(_(u"Can't remove temp directory"))

    def _onOk(self, event):
        self.resetLog()
        url = self._dialog.url

        if len(url) == 0:
            MessageBox(_('Enter link for downloading'),
                       _(u"Error"),
                       wx.ICON_ERROR | wx.OK)
            self._dialog.urlText.SetFocus()
            return

        if os.path.isfile(url):
            url = url.replace('\\', '/')
            if not url.startswith('/'):
                url = '/' + url

            url = 'file://' + url

        if self._thread is None:
            self._removeDownloadDir()
            self._downloadDir = mkdtemp(prefix='webpage_tmp_')

            self._runEvent.set()
            self._thread = DownloadThread(self._dialog,
                                          self._runEvent,
                                          self._downloadDir,
                                          url)
            self._thread.start()

    def _onCancel(self, event):
        self._runEvent.clear()
        if self._thread is not None:
            self._thread.join()

        self._removeDownloadDir()
        event.Skip()

    def _onSelectFile(self, event):
        with TestedFileDialog(
                self._dialog,
                wildcard=_("HTML files (*.html; *.htm)|*.html;*.htm|All files|*.*"),
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                self._dialog.url = fileDialog.GetPath()

    def _onDownloadError(self, event):
        self._onLogUpdate(event)
        self._thread = None
        self._removeDownloadDir()

    def _onDownloadFinish(self, event):
        self._thread = None
        if not self._runEvent.is_set():
            self.addToLog(_("Page creation is canceled."))
            self._removeDownloadDir()
            return

        parentPage = self._parentPage
        title = event.title if event.title is not None else _('Web page')
        favicon = event.favicon
        tags = self._dialog.tags
        content = event.content
        url = event.url
        tmpStaticDir = event.staticPath
        logContent = self._dialog.logText.Value

        titleDlg = wx.TextEntryDialog(self._dialog,
                                      _('Enter a title for the page'),
                                      _('Page title'),
                                      title)
        titleDlg.SetMinSize((450, 150))

        if titleDlg.ShowModal() == wx.ID_OK:
            title = titleDlg.GetValue()
        else:
            self.addToLog(_("Page creation is canceled."))
            self._removeDownloadDir()
            return

        try:
            page = WebPageFactory().createWebPage(parentPage,
                                                  title,
                                                  favicon,
                                                  tags,
                                                  content,
                                                  url,
                                                  tmpStaticDir,
                                                  logContent)
            self._dialog.EndModal(wx.ID_OK)
            self._application.selectedPage = page
        except EnvironmentError:
            self.addToLog(_("Can't create the page. Perhaps the title of the page is too long."))
        finally:
            self._removeDownloadDir()


class DownloadThread(Thread):
    def __init__(self, parentWnd, runEvent, downloadDir, url, name=None):
        super(DownloadThread, self).__init__(name=name)
        self._parentWnd = parentWnd
        self._runEvent = runEvent
        self._downloadDir = downloadDir
        self._url = url

        # Timeout in seconds
        self._timeout = 20

    def run(self):
        controller = WebPageDownloadController(
            self._runEvent,
            self._downloadDir,
            STATIC_DIR_NAME,
            self._parentWnd,
            self._timeout
        )

        downloader = Downloader(self._timeout)

        self._log(_('Start downloading\n'))

        try:
            downloader.start(self._url, controller)
        except urllib.error.URLError as error:
            self._error(_('Download error: {}\n').format(
                str(error.reason))
            )
        except(IOError, ValueError) as e:
            self._error(_('Invalid URL or file format\n'))
            self._error(str(e))
        else:
            self._log(_('Finish downloading\n'))

            content = downloader.contentResult
            staticPath = os.path.join(self._downloadDir, STATIC_DIR_NAME)
            title = downloader.pageTitle
            favicon = self._prepareFavicon(downloader.favicon)

            finishEvent = webpage.events.FinishDownloadEvent(
                content=content,
                staticPath=staticPath,
                title=title,
                favicon=favicon,
                url=self._url)
            wx.PostEvent(self._parentWnd, finishEvent)

    def _prepareFavicon(self, favicon_src):
        if favicon_src is not None:
            ico_ext = '.ico'
            png_ext = '.png'
            iconname = favicon_src[::-1].replace('.', '_16.'[::-1], 1)[::-1]
            if iconname.endswith(ico_ext):
                iconname = iconname[:-len(ico_ext)] + '.png'
                iconmaker = IconMaker()
                try:
                    iconmaker.create(favicon_src, iconname)
                    return iconname
                except IOError:
                    pass
            elif favicon_src.endswith(png_ext):
                return favicon_src

    def _log(self, text):
        event = webpage.events.UpdateLogEvent(text=text)
        wx.PostEvent(self._parentWnd, event)

    def _error(self, text):
        event = webpage.events.ErrorDownloadEvent(text=text)
        wx.PostEvent(self._parentWnd, event)
