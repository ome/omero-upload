#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   upload plugin

   Plugin read by omero.cli.Cli during initialization. The method(s)
   defined here will be added to the Cli class for later use.

   Copyright 2007-2016 Glencoe Software, Inc. All rights reserved.
   Use is subject to license terms supplied in LICENSE.txt

"""


import sys
from omero.cli import CLI
from omero_upload.cli import UploadControl, HELP

try:
    register("upload", UploadControl, HELP) # noqa
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("upload", UploadControl, HELP)
        cli.invoke(sys.argv[1:])
