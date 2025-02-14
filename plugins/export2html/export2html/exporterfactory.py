# -*- coding: utf-8 -*-

from .exceptions import InvalidPageFormat
from .htmlexporter import HtmlExporter
from .textexporter import TextExporter


class ExporterFactory:
    """
    Класс для экспорта страниц в HTML
    """
    @staticmethod
    def getExporter(page):
        exporter = None

        from .i18n import _
        global _

        if (page.getTypeString() == "html" or
                page.getTypeString() == "wiki" or
                page.getTypeString() == "markdown"):
            exporter = HtmlExporter(page)
        elif page.getTypeString() == "text":
            exporter = TextExporter(page)
        else:
            raise InvalidPageFormat (_("This page type not support export to HTML"))

        assert exporter is not None
        return exporter
