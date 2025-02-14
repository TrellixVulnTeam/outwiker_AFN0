# -*- coding: utf-8 -*-

import os
import shutil
import urllib.request
import urllib.error
import urllib.parse

from invoke import Context

from .base import BuilderBase
from buildtools.defines import (PLUGINS_DIR,
                                PLUGINS_LIST)
from buildtools.versions import (readAppInfo,
                                 getPluginInfoPath,
                                 getPluginChangelogPath,
                                 downloadAppInfo)


class BuilderPlugins(BuilderBase):
    """
    Create archives with plug-ins
    """

    def __init__(self,
                 c: Context,
                 updatedOnly: bool = False,
                 build_dir: str = PLUGINS_DIR,
                 plugins_list=None):
        super().__init__(c, build_dir)
        self._all_plugins_fname = u'outwiker-plugins-all.zip'
        self._plugins_list = (plugins_list if plugins_list is not None
                              else PLUGINS_LIST)
        self._updatedOnly = updatedOnly

    def get_plugins_pack_path(self):
        return self._getSubpath(self._all_plugins_fname)

    def clear(self):
        super(BuilderPlugins, self).clear()
        self._remove(self.get_plugins_pack_path())

    def _build(self):
        # Path to archive with all plug-ins
        full_archive_path = self.get_plugins_pack_path()

        for plugin in self._plugins_list:
            # Path to versions.xml for current plugin
            xmlinfo_path = getPluginInfoPath(plugin)
            changelog_path = getPluginChangelogPath(plugin)

            localAppInfo = readAppInfo(xmlinfo_path)
            assert localAppInfo is not None
            assert localAppInfo.version is not None

            skip_plugin = False

            # Check for update
            if self._updatedOnly:
                url = localAppInfo.updatesUrl
                try:
                    siteappinfo = downloadAppInfo(url)
                    if localAppInfo.version == siteappinfo.version:
                        skip_plugin = True
                except (urllib.error.URLError, urllib.error.HTTPError):
                    pass

            # Archive a single plug-in
            if not skip_plugin:
                version = str(localAppInfo.version)
                archive_name = u'{}-{}.zip'.format(plugin, version)

                # Subpath to current plug-in archive
                plugin_dir_path = self._getSubpath(plugin)

                # Path to future archive
                archive_path = self._getSubpath(plugin, archive_name)
                os.mkdir(plugin_dir_path)
                shutil.copy(xmlinfo_path, plugin_dir_path)
                shutil.copy(changelog_path, plugin_dir_path)

                # Archive a single plug-in
                with self.context.cd("plugins/{}".format(plugin)):
                    self.context.run(
                        '7z a -r -aoa -xr!*.pyc -xr!.ropeproject -x!doc -x!versions.xml "{}" ./*'.format(archive_path))

            # Add a plug-in to full archive
            with self.context.cd("plugins/{}".format(plugin)):
                self.context.run(
                    '7z a -r -aoa -xr!*.pyc -xr!.ropeproject -x!versions.xml -w../ "{}" ./*'.format(full_archive_path))

    def _getSubpath(self, *args):
        """
        Return subpath inside current build path (inside 'build' subpath)
        """
        return os.path.join(self.build_dir, *args)
