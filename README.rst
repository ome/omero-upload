.. image:: https://travis-ci.org/ome/omero-upload.svg?branch=master
    :target: https://travis-ci.org/ome/omero-upload

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
