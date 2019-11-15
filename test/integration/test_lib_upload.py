#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2019 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from builtins import str
import pytest
import os

import omero
from omero.testlib import ITest
from omero_upload import upload_ln_s
from omero.util.temp_files import create_path
from omero.util import long_to_path


class TestLibUpload(ITest):

    def test_upload_ln_s(self):
        txt = 'hello\n'
        omero_data_dir = self.root.sf.getConfigService().getConfigValue(
            'omero.data.dir')
        assert omero_data_dir
        f = create_path(suffix=".txt")
        f.write_text(txt)
        ofile = upload_ln_s(self.client, f, omero_data_dir, 'text/plain')
        assert ofile.getHash() == 'f572d396fae9206628714fb2ce00f72e94f2258f'
        assert ofile.getSize() == 6
        with ofile.asFileObj() as fo:
            assert fo.read().decode('utf-8') == txt

        omero_path = os.path.join(
            omero_data_dir, 'Files', long_to_path(ofile.id))
        assert os.path.islink(omero_path)
        assert os.readlink(omero_path) == str(f)

    def test_upload_ln_s_no_access(self):
        txt = 'hello\n'
        omero_data_dir = '/tmp'
        f = create_path(suffix=".txt")
        f.write_text(txt)
        with pytest.raises(omero.ApiUsageException):
            upload_ln_s(self.client, f, omero_data_dir, 'text/plain')
