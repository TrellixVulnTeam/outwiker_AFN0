# -*- coding: utf-8 -*-
"""
Модуль с классом диалога настроек
"""

import wx

from outwiker.gui.testeddialog import TestedDialog


class PrefDialog(TestedDialog):
    """
    Класс диалога настроек
    """

    def __init__(self, parent, application):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(PrefDialog, self).__init__(parent, style=style)
        self._application = application
        self.__treeBook = wx.Treebook(self, -1)
        self.__do_layout()
        self._application.onPreferencesDialogCreate(self)

    @property
    def treeBook(self):
        """
        Возвращает указатель на дерево с панелями,
        который должен быть родителем для панелей с настройками
        """
        return self.__treeBook

    @property
    def pages(self):
        count = self.__treeBook.GetPageCount()
        for n in range(count):
            yield self.__treeBook.GetPage(n)

    @property
    def currentPage(self):
        return self.__treeBook.GetCurrentPage()

    def appendPreferenceGroup(self, groupname, prefPanelsInfoList):
        """
        Добавить группу настроек
        groupname - имя группы
        prefPanelsInfoList - массив экземпляров класса PreferencePanelInfo

        Страница корня группы - первая страница в списке панелей.
        Массив не должен быть пустым
        """
        assert len(prefPanelsInfoList) != 0
        self.__treeBook.AddPage(prefPanelsInfoList[0].panel, groupname)

        # Если всего одна страница в списке,
        # то не будем добавлять вложенные страницы
        if len(prefPanelsInfoList) > 1:
            for panelInfo in prefPanelsInfoList:
                self.__treeBook.AddSubPage(panelInfo.panel, panelInfo.name)

    def __do_layout(self):
        main_sizer = wx.FlexGridSizer(cols=1)
        main_sizer.AddGrowableRow(0)
        main_sizer.AddGrowableCol(0)
        main_sizer.Add(self.__treeBook, 0, wx.ALL | wx.EXPAND, 4)

        self.__createOkCancelButtons(main_sizer)

        self.SetSizer(main_sizer)
        self.Layout()

    def __createOkCancelButtons(self, sizer):
        """
        Создать кнопки Ok / Cancel
        """
        buttonsSizer = self.CreateButtonSizer(wx.OK | wx.CANCEL | wx.HELP)
        sizer.Add(buttonsSizer,
                  0,
                  wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM | wx.ALL,
                  border=4)
