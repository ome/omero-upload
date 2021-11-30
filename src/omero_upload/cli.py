#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2019 Glencoe Software, Inc & University of Dundee.
# All rights reserved.
#
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import re
import mimetypes

from omero.cli import BaseControl
from omero.model import FileAnnotationI, OriginalFileI
from omero.rtypes import rstring
from .library import upload_ln_s

try:
    from omero_ext.path import path
except ImportError:
    # Python 2
    from path import path


HELP = """Upload local files to the OMERO server"""
RE = re.compile(r"\s*upload\s*")
UNKNOWN = 'type/unknown'


class UploadControl(BaseControl):

    def _complete(self, text, line, begidx, endidx):
        """
        Returns a file after "upload" and otherwise delegates to the
        BaseControl
        """
        m = RE.match(line)
        if m:
            return self._complete_file(RE.sub('', line))
        else:
            return BaseControl._complete(self, text, line, begidx, endidx)

    def _configure(self, parser):
        parser.add_argument("file", nargs="+")
        parser.add_argument(
            "-m", "--mimetype", help="Mimetype of the file")
        parser.add_argument(
            "--data-dir", type=str,
            help="Path to the OMERO data directory. If passed will try to "
            "in-place upload into ManagedRepository")
        parser.add_argument(
            "--wrap", action="store_true",
            help="Wrap the original file into a File Annotation")
        parser.add_argument(
            "--namespace", type=str,
            help="Specifies the FileAnnotation namespace (requires --wrap)")
        parser.set_defaults(func=self.upload)
        parser.add_login_arguments()

    def upload(self, args):
        client = self.ctx.conn(args)
        obj_ids = []
        for local_file in args.file:
            if not path(local_file).exists():
                self.ctx.die(500, "File: %s does not exist" % local_file)
        for local_file in args.file:
            omero_format = UNKNOWN
            if args.mimetype:
                omero_format = args.mimetype
            elif (mimetypes.guess_type(local_file) != (None, None)):
                omero_format = mimetypes.guess_type(local_file)[0]
            if args.data_dir:
                obj = upload_ln_s(
                    client, local_file, args.data_dir, omero_format)
                obj_id = obj.id
            else:
                obj = client.upload(local_file, type=omero_format)
                obj_id = obj.id.val
            if args.wrap:
                fa = FileAnnotationI()
                fa.setFile(OriginalFileI(obj_id, False))
                if args.namespace:
                    fa.setNs(rstring(args.namespace))
                fa = client.sf.getUpdateService().saveAndReturnObject(fa)
                obj_ids.append(fa.id.val)
            else:
                obj_ids.append(obj_id)
            self.ctx.set("last.upload.id", obj_id)

        obj_ids = self._order_and_range_ids(obj_ids)
        if args.wrap:
            self.ctx.out("FileAnnotation:%s" % obj_ids)
        else:
            self.ctx.out("OriginalFile:%s" % obj_ids)
