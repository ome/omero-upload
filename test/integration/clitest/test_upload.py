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
from omero_upload.cli import UploadControl
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

    def get_objects(self, out):
        objects = []
        for i in out.split(":")[1].split(","):
            objects.append(self.query.get(out.split(":")[0], int(i)))
        return objects

    def is_symlink(self, original_file):
        file_id = original_file.id.val
        omero_path = os.path.join("/OMERO", 'Files', long_to_path(file_id))
        assert os.path.exists(omero_path)
        return os.path.islink(omero_path)

    def test_upload_single_file(self, capfd):
        f = create_path(suffix=".txt")
        self.args += [str(f)]
        out = self.upload(capfd)
        assert out.startswith("OriginalFile:")
        objects = self.get_objects(out)
        assert len(objects) == 1
        assert objects[0].name.val == f.name

    @pytest.mark.parametrize('ln_s', [True, False])
    def test_upload_multiple_files(self, capfd, ln_s):
        f1 = create_path(suffix=".txt")
        f2 = create_path(suffix=".txt")
        self.args += [str(f1), str(f2)]
        if ln_s:
            self.args += ["--data-dir", "/OMERO"]
        out = self.upload(capfd)
        assert out.startswith("OriginalFile:")
        objects = self.get_objects(out)
        assert len(objects) == 2
        assert objects[0].name.val == f1.name
        assert objects[1].name.val == f2.name
        if ln_s:
            assert self.is_symlink(objects[0])
            assert self.is_symlink(objects[1])
        else:
            assert not self.is_symlink(objects[0])
            assert not self.is_symlink(objects[1])

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
        assert out.startswith("OriginalFile:")
        objects = self.get_objects(out)
        assert len(objects) == 1
        assert objects[0].name.val == f.name
        assert objects[0].mimetype.val == "text/plain"

    @pytest.mark.parametrize('ln_s', [True, False])
    def test_mimetype_argument(self, capfd, ln_s):
        f = create_path(suffix=".txt")
        self.args += [str(f), "--mimetype", "text/csv"]
        if ln_s:
            self.args += ["--data-dir", "/OMERO"]
        out = self.upload(capfd)
        assert out.startswith("OriginalFile:")
        objects = self.get_objects(out)
        assert len(objects) == 1
        assert objects[0].name.val == f.name
        assert objects[0].mimetype.val == "text/csv"
        if ln_s:
            assert self.is_symlink(objects[0])
        else:
            assert not self.is_symlink(objects[0])

    @pytest.mark.parametrize('ln_s', [True, False])
    @pytest.mark.parametrize('ns', [None, 'foo'])
    @pytest.mark.parametrize('mimetype', [None, "text/csv"])
    def test_file_annotation(self, capfd, ns, ln_s, mimetype):
        f = create_path(suffix=".txt")
        self.args += [str(f), "--wrap"]
        if ns is not None:
            self.args += ["--namespace", ns]
        if ln_s:
            self.args += ["--data-dir", "/OMERO"]
        if mimetype:
            self.args += ["--mimetype", mimetype]
        out = self.upload(capfd)
        assert out.startswith("FileAnnotation:")
        objects = self.get_objects(out)
        assert len(objects) == 1
        if ns:
            assert objects[0].ns.val == ns
        else:
            assert not objects[0].ns
        original_file = self.query.get('OriginalFile', objects[0].file.id.val)
        assert original_file.name.val == f.name
        if mimetype:
            assert original_file.mimetype.val == mimetype
        else:
            assert original_file.mimetype.val == "text/plain"
        if ln_s:
            assert self.is_symlink(original_file)
        else:
            assert not self.is_symlink(original_file)

    def test_multiple_fileannotations(self, capfd):
        f1 = create_path(suffix=".txt")
        f2 = create_path(suffix=".txt")
        self.args += [str(f1), str(f2), "--wrap"]
        out = self.upload(capfd)
        assert out.startswith("FileAnnotation:")
        objects = self.get_objects(out)
        assert len(objects) == 2
        original_file = self.query.get('OriginalFile', objects[0].file.id.val)
        assert original_file.name.val == f1.name
        assert not self.is_symlink(original_file)
        original_file = self.query.get('OriginalFile', objects[1].file.id.val)
        assert original_file.name.val == f2.name
        assert not self.is_symlink(original_file)
