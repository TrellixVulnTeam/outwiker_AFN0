# -*- coding: utf-8 -*-

import unittest
import os
import os.path
from tempfile import mkdtemp

from outwiker.pages.wiki.thumbnails import Thumbnails
from outwiker.tests.utils import removeDir
from outwiker.core.tree import WikiDocument
from outwiker.pages.wiki.parserfactory import ParserFactory
from outwiker.pages.wiki.wikipage import WikiPageFactory
from outwiker.core.application import Application
from outwiker.core.attachment import Attachment


class ThumbnailsTest(unittest.TestCase):
    def setUp(self):
        self.filesPath = "testdata/samplefiles/"
        self.__createWiki()
        self.parser = ParserFactory().make(self.testPage, Application.config)

    def __createWiki(self):
        # Здесь будет создаваться вики
        self.path = mkdtemp(prefix='Абырвалг абыр')

        self.wikiroot = WikiDocument.create(self.path)
        WikiPageFactory().create(self.wikiroot, "Страница 2", [])
        self.testPage = self.wikiroot["Страница 2"]

    def tearDown(self):
        removeDir(self.path)

    def testThumbnails1(self):
        thumb = Thumbnails(self.parser.page)
        thumbDir = thumb.getThumbPath(create=False)

        self.assertEqual(
            thumbDir,
            os.path.join(Attachment(self.parser.page).getAttachPath(),
                         Thumbnails.thumbDir),
            thumbDir)

    def testThumbnails2(self):
        thumb = Thumbnails(self.parser.page)
        thumbDir = thumb.getThumbPath(create=False)

        self.assertFalse(os.path.exists(thumbDir))

    def testThumbnails3(self):
        thumb = Thumbnails(self.parser.page)
        thumbDir = thumb.getThumbPath(create=True)

        self.assertTrue(os.path.exists(thumbDir))

    def testThumbnailsClear1(self):
        thumb = Thumbnails(self.parser.page)
        thumb.clearDir()

        self.assertFalse(os.path.exists(thumb.getThumbPath(create=False)))

    def testThumbnails1_attach(self):
        thumb = Thumbnails(self.parser.page)
        thumbDir = thumb.getThumbPath(create=False)

        self.assertEqual(
            thumbDir,
            os.path.join(Attachment(self.parser.page).getAttachPath(),
                         Thumbnails.thumbDir),
            thumbDir)

    def testThumbnails2_attach(self):
        fname = "accept.png"
        attachPath = os.path.join(self.filesPath, fname)
        Attachment(self.parser.page).attach([attachPath])

        thumb = Thumbnails(self.parser.page)
        thumbDir = thumb.getThumbPath(create=False)

        self.assertFalse(os.path.exists(thumbDir))

    def testThumbnails3_attach(self):
        fname = "accept.png"
        attachPath = os.path.join(self.filesPath, fname)
        Attachment(self.parser.page).attach([attachPath])

        thumb = Thumbnails(self.parser.page)
        thumbDir = thumb.getThumbPath(create=True)

        self.assertTrue(os.path.exists(thumbDir))

    def testThumbnailsClear1_attach(self):
        fname = "accept.png"
        attachPath = os.path.join(self.filesPath, fname)
        Attachment(self.parser.page).attach([attachPath])

        thumb = Thumbnails(self.parser.page)
        thumb.clearDir()

        self.assertFalse(os.path.exists(thumb.getThumbPath(create=False)))
