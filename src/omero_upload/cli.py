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
import path
import mimetypes

from omero.cli import BaseControl


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
        parser.set_defaults(func=self.upload)
        parser.add_login_arguments()

    def upload(self, args):
        client = self.ctx.conn(args)
        obj_ids = []
        for file in args.file:
            if not path.path(file).exists():
                self.ctx.die(500, "File: %s does not exist" % file)
        for file in args.file:
            omero_format = UNKNOWN
            if(mimetypes.guess_type(file) != (None, None)):
                omero_format = mimetypes.guess_type(file)[0]
            obj = client.upload(file, type=omero_format)
            obj_ids.append(obj.id.val)
            self.ctx.set("last.upload.id", obj.id.val)

        obj_ids = self._order_and_range_ids(obj_ids)
        self.ctx.out("OriginalFile:%s" % obj_ids)
