.. image:: https://github.com/ome/omero-upload/workflows/OMERO/badge.svg
    :target: https://github.com/ome/omero-upload/actions

.. image:: https://badge.fury.io/py/omero-upload.svg
    :target: https://badge.fury.io/py/omero-upload

OMERO CLI upload
================

Plugin for uploading files using the OMERO Command Line Interface (CLI).

Requirements
------------

* OMERO 5.6.0 or newer
* Python 3.6 or newer

Installing from PyPI
--------------------

This section assumes that an OMERO.py is already installed.

Install the command-line tool using `pip <https://pip.pypa.io/en/stable/>`_::

    $ pip install -U omero-upload

Usage
-----

The plugin is called from the command-line using the `omero` command.

To upload a single file::

    $ omero upload <file>

This command will create an `OriginalFile` on the server and return an output
of type `OriginalFile:<id>`.

To upload multiple files::

    $ omero upload <file1> <file2>

This command will create two `OriginalFile` and return an output of type `OriginalFile:<id1>,<id2>`

By default, the mimetype will be guessed from the filename but it can be
specified by using the `--mimetype` argument::

    $ omero upload <file1> --mimetype 'test/csv'

Files can be in-place uploaded into the OMERO.server via symlinked rather than
being copied. This requires the command to be run on the OMERO.server itself
from a user having write permissions to the OMERO data repository, similarly
to the [in-place import](https://docs.openmicroscopy.org/omero/latest/sysadmins/in-place-import.html). To run an in-place upload, the `--data-dir` argument must be passed to
specify the binary OMERO directory::

    $ omero upload <file1> --data-dir /OMERO

Instead of creating and returning a simple `OriginalFile` object, it is also possible to wrap the file within a `FileAnnotation` which can then be linked
to other objects in the database. It is possible to specify the namespace of this `FileAnnotation` using the `--namespace` argument::


    $ omero upload <file1> --wrap --namespace 'openmicroscopy.org/idr/analysis/original'

This command will create an `OriginalFile` and a `FileAnnotation` and return
an output of type `FileAnnotation:<id>`.

Release process
---------------

This repository uses `bump2version <https://pypi.org/project/bump2version/>`_ to manage version numbers.
To tag a release run::

    $ bumpversion release

This will remove the ``.dev0`` suffix from the current version, commit, and tag the release.

To switch back to a development version run::

    $ bumpversion --no-tag [major|minor|patch]

specifying ``major``, ``minor`` or ``patch`` depending on whether the development branch will be a `major, minor or patch release <https://semver.org/>`_. This will also add the ``.dev0`` suffix.

Remember to ``git push`` all commits and tags.

License
-------

This project, similar to many Open Microscopy Environment (OME) projects, is
licensed under the terms of the GNU General Public License (GPL) v2 or later.

Copyright
---------

2019-2020, The Open Microscopy Environment
