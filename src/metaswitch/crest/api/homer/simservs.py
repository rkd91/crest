# @file simservs.py
#
# Copyright (C) 2013  Metaswitch Networks Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# The author can be reached by email at clearwater@metaswitch.com or by post at
# Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK


import logging
import os

from lxml import etree
from cyclone.web import HTTPError

from metaswitch.crest.api.passthrough import PassthroughHandler
from metaswitch.crest.api import xsd

SCHEMA_NAME = "mmtel.xsd"
SCHEMA_DIR_NAME = "schema"
SCHEMA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), SCHEMA_DIR_NAME)
SCHEMA_PATH = os.path.join(SCHEMA_DIR, SCHEMA_NAME)

_log = logging.getLogger("crest.api.homer")

class SimservsHandler(PassthroughHandler):
    """
    Handler that validates simservs documents before storing them
    """
    @xsd.validate(SCHEMA_PATH)
    def put(self, *args):
        PassthroughHandler.put(self, *args)
