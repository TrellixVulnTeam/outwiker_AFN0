# -*- coding: utf-8 -*-

import unittest
from tempfile import mkdtemp

from outwiker.core.pageuiddepot import PageUidDepot
from outwiker.core.commands import generateLink
from outwiker.core.tree import WikiDocument
from outwiker.core.application import Application
from outwiker.core.exceptions import ReadonlyException
from outwiker.pages.text.textpage import TextPageFactory
from outwiker.tests.utils import removeDir


class PageUidDepotTest(unittest.TestCase):
    """Тест класса PageUidDepot"""

    def setUp(self):
        # Здесь будет создаваться вики
        self.path = mkdtemp(prefix='Абырвалг абыр')

        self.wikiroot = WikiDocument.create(self.path)

        factory = TextPageFactory()
        factory.create(self.wikiroot, "Страница 1", [])
        factory.create(self.wikiroot, "Страница 2", [])
        factory.create(self.wikiroot["Страница 2"], "Страница 3", [])
        factory.create(self.wikiroot["Страница 2/Страница 3"],
                       "Страница 4",
                       [])
        factory.create(self.wikiroot["Страница 1"], "Страница 5", [])

        Application.wikiroot = None

    def tearDown(self):
        Application.wikiroot = None
        removeDir(self.path)

    def testEmpty(self):
        depot = PageUidDepot()
        self.assertEqual(depot["Абырвалг"], None)

    def testCreateUid_01(self):
        depot = PageUidDepot()
        uid = depot.createUid(self.wikiroot["Страница 1"])
        self.assertEqual(depot[uid], self.wikiroot["Страница 1"])

    def testCreateUid_02(self):
        depot = PageUidDepot()
        uid = depot.createUid(self.wikiroot["Страница 1"])
        uid_new = depot.createUid(self.wikiroot["Страница 1"])

        self.assertEqual(uid, uid_new)

    def testCreateUid_03(self):
        depot = PageUidDepot()
        uid = depot.createUid(self.wikiroot["Страница 1"])
        self.assertEqual(depot[uid.upper()], self.wikiroot["Страница 1"])

    def testSaveLoad_01(self):
        depot = PageUidDepot()
        uid = depot.createUid(self.wikiroot["Страница 1"])

        depot_new = PageUidDepot(self.wikiroot)

        self.assertEqual(depot_new[uid].title, "Страница 1")

    def testSaveLoad_02(self):
        depot = PageUidDepot()
        uid = depot.createUid(
            self.wikiroot["Страница 2/Страница 3/Страница 4"]
        )

        depot_new = PageUidDepot(self.wikiroot)

        self.assertEqual(depot_new[uid].title, "Страница 4")

    def testSaveLoad_03(self):
        depot = PageUidDepot()
        uid = depot.createUid(self.wikiroot["Страница 1"])

        depot_new = PageUidDepot(self.wikiroot)

        self.assertEqual(depot_new[uid].title, "Страница 1")

        removeDir(self.path)

    def testRenamePage(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]
        uid = depot.createUid(page)

        page.title = "Новый заголовок"
        self.assertEqual(depot[uid].title, "Новый заголовок")

        depot_new = PageUidDepot(self.wikiroot)
        self.assertEqual(depot_new[uid].title, "Новый заголовок")

    def testRemovePage(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]
        uid = depot.createUid(page)

        page.remove()
        self.assertEqual(depot[uid], None)

    def testMovePage(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]
        uid = depot.createUid(page)

        page.moveTo(self.wikiroot)
        self.assertEqual(depot[uid].title, "Страница 3")

        depot_new = PageUidDepot(self.wikiroot)
        self.assertEqual(depot_new[uid].title, "Страница 3")
        self.assertEqual(depot_new[uid].parent, self.wikiroot)

    def testChangeUid_01(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "Абырвалг"
        depot.changeUid(page, new_uid)

        self.assertEqual(depot[new_uid].title, "Страница 3")

        depot_new = PageUidDepot(self.wikiroot)
        self.assertEqual(depot_new[new_uid].title, "Страница 3")

    def testChangeUid_02(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "Абырвалг"
        depot.changeUid(page, new_uid)
        depot.changeUid(page, new_uid)

        self.assertEqual(depot[new_uid].title, "Страница 3")

    def testChangeUid_03(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "Абырвалг"
        depot.changeUid(page, new_uid)

        self.assertRaises(KeyError,
                          depot.changeUid,
                          self.wikiroot["Страница 1"],
                          new_uid)

    def testChangeUid_04(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "Абырвалг"
        depot.changeUid(page, new_uid)

        self.assertRaises(ValueError,
                          depot.changeUid,
                          self.wikiroot["Страница 1"],
                          "")

    def testChangeUid_05(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "Абырвалг"
        depot.changeUid(page, new_uid)

        page.remove()
        self.assertEqual(depot[new_uid], None)

    def testChangeUid_06(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "  "
        self.assertRaises(ValueError,
                          depot.changeUid,
                          page,
                          new_uid)

    def testChangeUid_07(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        # Запрещено использовать "/" в идентификаторах
        new_uid = "Абырвалг/фвыафыва"
        self.assertRaises(ValueError,
                          depot.changeUid,
                          page,
                          new_uid)

    def testChangeUid_08(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "Абырвалг"
        depot.changeUid(page, new_uid)

        self.assertRaises(KeyError,
                          depot.changeUid,
                          self.wikiroot["Страница 1"],
                          "абырвалг")

    def testChangeUid_09(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]

        new_uid = "АБЫРВАЛГ"
        depot.changeUid(page, new_uid)

        self.assertEqual(depot["абырвалг"].title, "Страница 3")

    def testChangeUid_10(self):
        depot = PageUidDepot()

        new_uid = "Абырвалг"
        depot.changeUid(self.wikiroot["Страница 2/Страница 3"], new_uid)

        depot2 = PageUidDepot()
        depot2.changeUid(self.wikiroot["Страница 2"], new_uid)

        depot3 = PageUidDepot(self.wikiroot)
        self.assertEqual(depot3[new_uid].title, "Страница 3")

    def testApplication_01(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]
        uid = depot.createUid(page)

        Application.wikiroot = self.wikiroot

        self.assertEqual(Application.pageUidDepot[uid].title, "Страница 3")

    def testApplication_02(self):
        Application.wikiroot = self.wikiroot

        page = self.wikiroot["Страница 2/Страница 3"]
        uid = Application.pageUidDepot.createUid(page)

        Application.wikiroot = None
        Application.wikiroot = self.wikiroot

        self.assertEqual(Application.pageUidDepot[uid].title, "Страница 3")

    def testApplicationRenamePage(self):
        Application.wikiroot = self.wikiroot

        page = self.wikiroot["Страница 2/Страница 3"]
        uid = Application.pageUidDepot.createUid(page)

        page.title = "Новый заголовок"
        self.assertEqual(Application.pageUidDepot[uid].title,
                         "Новый заголовок")

    def testApplicationRemovePage(self):
        Application.wikiroot = self.wikiroot

        page = self.wikiroot["Страница 2/Страница 3"]
        uid = Application.pageUidDepot.createUid(page)

        page.remove()
        self.assertEqual(Application.pageUidDepot[uid], None)

    def testApplicationMovePage(self):
        Application.wikiroot = self.wikiroot

        page = self.wikiroot["Страница 2/Страница 3"]
        uid = Application.pageUidDepot.createUid(page)

        page.moveTo(self.wikiroot)
        self.assertEqual(Application.pageUidDepot[uid].title, "Страница 3")
        self.assertEqual(Application.pageUidDepot[uid].parent, self.wikiroot)

    def testGenerateLink_01(self):
        Application.wikiroot = self.wikiroot
        page = self.wikiroot["Страница 2/Страница 3"]
        uid = Application.pageUidDepot.createUid(page)

        link = generateLink(Application, page)
        self.assertIn("page://", link)
        self.assertIn(uid, link)

    def testGenerateLink_02(self):
        Application.wikiroot = self.wikiroot
        page = self.wikiroot["Страница 2/Страница 3"]

        newUid = "Абырвалг"
        Application.pageUidDepot.changeUid(page, newUid)

        link = generateLink(Application, page)
        self.assertIn("page://", link)
        self.assertIn("абырвалг", link)

    def testGenerateLink_03(self):
        Application.wikiroot = self.wikiroot
        page = self.wikiroot["Страница 2/Страница 3"]
        Application.pageUidDepot.createUid(page)

        newUid = "Абырвалг"
        Application.pageUidDepot.changeUid(page, newUid)

        link = generateLink(Application, page)
        self.assertIn("page://", link)
        self.assertIn("абырвалг", link)

    def testReadOnly_01(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]
        page.readonly = True

        self.assertRaises(ReadonlyException, depot.createUid, page)

    def testReadOnly_02(self):
        depot = PageUidDepot()
        page = self.wikiroot["Страница 2/Страница 3"]
        depot.createUid(page)

        page.readonly = True

        depot.createUid(page)
