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

from hashlib import sha1
import logging
import os
from StringIO import StringIO
import omero.clients
from omero.gateway import BlitzGateway

log = logging.getLogger(__name__)

bufsize = 1048576


def upload_ln_s(client, filepath, omero_data_dir, mimetype=None):
    """
    Simulate an in-place ln-s upload by creating an empty file, replacing it
    with a symlink, and updating the OriginalFile metadata.

    Requires write access to the omero.data.dir Files directory

    :param client: Connected client object
    :param filepath: Path to the file to be symlinked into OMERO
    :param omero_data_dir: The OMERO data directory
    :param mimetype: The mimetype to be assigned to the file in OMERO
    :return: The wrapped OriginalFile for the symlinked file
    """
    abspath = os.path.abspath(filepath)
    filedir = os.path.dirname(abspath)
    filename = os.path.basename(abspath)

    conn = BlitzGateway(client_obj=client)

    log.debug('Creating empty OriginalFile placeholder')
    placeholder = StringIO('')
    fo = conn.createOriginalFileFromFileObj(
        placeholder, filedir, filename, 0, mimetype=mimetype)
    omero_path = os.path.join(
        omero_data_dir, 'Files', omero.util.long_to_path(fo.id))

    log.debug('OriginalFile:%d Deleting %s', fo.id, omero_path)
    try:
        os.remove(omero_path)
    except OSError:
        log.error(
            'Unable to delete, do you have direct access to the OMERO '
            'filesystem? %s', omero_path)
        log.debug('Attempting to clean up OriginalFile:%d', fo.id)
        conn.deleteObject(fo._obj)
        raise

    log.debug('OriginalFile:%d Symlinking %s to %s',
              fo.id, abspath, omero_path)
    os.symlink(abspath, omero_path)

    log.debug('OriginalFile:%d Getting size and checksum', fo.id)
    size = os.path.getsize(abspath)
    h = sha1()
    with open(abspath) as f:
        while True:
            data = f.read(bufsize)
            if not data:
                break
            h.update(data)
    hash = h.hexdigest()

    log.debug('OriginalFile:%d Saving size:%d and checksum:%s',
              fo.id, size, hash)
    fo.setSize(omero.rtypes.rlong(size))
    fo.setHash(omero.rtypes.rstring(hash))
    chk = omero.model.ChecksumAlgorithmI()
    chk.setValue(omero.rtypes.rstring(
        omero.model.enums.ChecksumAlgorithmSHA1160))
    fo.setHasher(chk)
    fo.save()
    return fo
