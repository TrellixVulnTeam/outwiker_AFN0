# coding: utf-8

from typing import List, TextIO
import xml.etree.ElementTree as ET

from .baseupdater import BaseUpdater


class VersionsXmlUpdater(BaseUpdater):
    """Update version information in versions.xml file."""

    def __init__(self):
        self._versions_tag = '<versions>\n'
        self._new_version_tpl = """<versions>
    <version number="{version}"{status}>
        <changes>
        </changes>

        <changes lang="ru">
        </changes>
    </version>

"""
        self.status_tag_attrib_name = 'status'

    def set_version(self, input_text: TextIO,
                    version: List[int],
                    status: str = '') -> str:
        tree = ET.parse(input_text)
        root = tree.getroot()
        version_tag = root.find('version')

        version_str = '.'.join([str(item) for item in version])
        version_tag.set('number', version_str)

        if status:
            version_tag.set(self.status_tag_attrib_name, status)
        else:
            if self.status_tag_attrib_name in version_tag.attrib:
                del version_tag.attrib[self.status_tag_attrib_name]

        return ET.tostring(root,
                           encoding='UTF-8',
                           xml_declaration=True).decode()

    def add_version(self, input_text: TextIO,
                    version: List[int],
                    status: str = '') -> str:
        version_str = '.'.join([str(item) for item in version])
        status_str = ' status="{}"'.format(status) if status else ''

        new_version_tag = self._new_version_tpl.format(version=version_str,
                                                       status=status_str)
        return input_text.read().replace(self._versions_tag, new_version_tag)

    def set_release_date(self, input_text: TextIO, date_str: str) -> str:
        assert False
