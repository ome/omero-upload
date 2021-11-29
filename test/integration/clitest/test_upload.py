#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (C) 2016 University of Dundee & Open Microscopy Environment.
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
import os.path
import pytest

from omero.testlib.cli import CLITest
from omero.cli import NonZeroReturnCode
from omero.plugins.obj import ObjControl
from omero.plugins.upload import UploadControl
from omero.util.temp_files import create_path
from omero.util import long_to_path


class TestUpload(CLITest):

    def setup_method(self, method):
        super(TestUpload, self).setup_method(method)
        self.cli.register("upload", UploadControl, "TEST")
        self.cli.register("obj", ObjControl, "TEST")
        self.args += ["upload"]

    def upload(self, capfd):
        self.cli.invoke(self.args, strict=True)
        return capfd.readouterr()[0]

    def check_file_name(self, original_file, filename):
        args = self.login_args() + ["obj", "get", original_file]
        self.cli.invoke(args + ["name"], strict=True)
        name = self.cli.get("tx.state").get_row(0)
        assert filename.name == name

    def check_mimetype(self, original_file, expected_mimetype):
        args = self.login_args() + ["obj", "get", original_file]
        self.cli.invoke(args + ["mimetype"], strict=True)
        mimetype = self.cli.get("tx.state").get_row(0)
        assert mimetype == expected_mimetype

    def check_file_path(self, original_file, is_link):
        file_id = int(original_file.split(":")[1])
        omero_path = os.path.join("/OMERO", 'Files', long_to_path(file_id))
        assert os.path.exists(omero_path)
        if is_link:
            assert os.path.islink(omero_path)
        else:
            assert not os.path.islink(omero_path)

    def test_upload_single_file(self, capfd):
        f = create_path(suffix=".txt")
        self.args += [str(f)]
        out = self.upload(capfd)
        self.check_file_name(out, f)

    @pytest.mark.parametrize('ln_s', [True, False])
    def test_upload_multiple_files(self, capfd, ln_s):
        f1 = create_path(suffix=".txt")
        f2 = create_path(suffix=".txt")
        self.args += [str(f1), str(f2)]
        if ln_s:
            self.args += ["--data-dir", "/OMERO"]
        out = self.upload(capfd)
        ids = out.split(":")[1].split(",")
        self.check_file_name("OriginalFile:%s" % ids[0], f1)
        self.check_file_name("OriginalFile:%s" % ids[1], f2)

    def test_upload_bad_file(self, capfd):
        f1 = create_path(suffix=".txt")
        f2 = self.uuid() + ""
        self.args += [str(f1), str(f2)]
        with pytest.raises(NonZeroReturnCode):
            self.upload(capfd)

    def test_guessed_mimetype(self, capfd):
        f = create_path(suffix=".txt")
        self.args += [str(f)]
        out = self.upload(capfd)
        self.check_file_name(out, f)
        self.check_mimetype(out, "text/plain")

    @pytest.mark.parametrize('ln_s', [True, False])
    def test_mimetype_argument(self, capfd, ln_s):
        f = create_path(suffix=".txt")
        self.args += [str(f), "--mimetype", "text/csv"]
        if ln_s:
            self.args += ["--data-dir", "/OMERO"]
        out = self.upload(capfd)
        self.check_file_name(out, f)
        self.check_mimetype(out, "text/csv")
        if ln_s:
            self.check_file_path(out, True)
        else:
            self.check_file_path(out, False)
