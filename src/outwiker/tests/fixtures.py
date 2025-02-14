# -*- coding=utf-8 -*-

from tempfile import mkdtemp

import pytest

from outwiker.core.tree import WikiDocument
from outwiker.pages.text.textpage import TextPageFactory
from outwiker.tests.utils import removeDir


@pytest.fixture
def wikipage():
    path = mkdtemp(prefix='outwiker_wiki')
    factory = TextPageFactory()
    wikiroot = WikiDocument.create(path)
    page = factory.create(wikiroot, "Страница 1", [])

    yield page

    removeDir(path)
