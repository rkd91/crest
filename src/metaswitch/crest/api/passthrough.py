# @file passthrough.py
#
# Project Clearwater - IMS in the Cloud
# Copyright (C) 2013  Metaswitch Networks Ltd
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version, along with the "Special Exception" for use of
# the program along with SSL, set forth below. This program is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details. You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
# The author can be reached by email at clearwater@metaswitch.com or by
# post at Metaswitch Networks Ltd, 100 Church St, Enfield EN2 6BQ, UK
#
# Special Exception
# Metaswitch Networks Ltd  grants you permission to copy, modify,
# propagate, and distribute a work formed by combining OpenSSL with The
# Software, or a work derivative of such a combination, even if such
# copying, modification, propagation, or distribution would otherwise
# violate the terms of the GPL. You must comply with the GPL in all
# respects for all of the code used other than OpenSSL.
# "OpenSSL" means OpenSSL toolkit software distributed by the OpenSSL
# Project and licensed under the OpenSSL Licenses, or a work based on such
# software and licensed under the OpenSSL Licenses.
# "OpenSSL Licenses" means the OpenSSL License and Original SSLeay License
# under which the OpenSSL Project distributes the OpenSSL toolkit software,
# as those licenses appear in the file LICENSE-OPENSSL.


import logging
import httplib

from cyclone.web import HTTPError
from telephus.client import CassandraClient
from telephus.cassandra.ttypes import NotFoundException
from twisted.internet import defer

from metaswitch.crest import settings
from metaswitch.crest.api._base import BaseHandler

_log = logging.getLogger("crest.api")

class PassthroughHandler(BaseHandler):
    """
    The passthrough handler simply takes what has been sent in from the router
    and reads/writes/deletes without any validation.

    Handlers should subclass this handler in order to do parameter validation. After
    validation, the handlers should call through the passthrough handler to write to the
    database
    """

    def initialize(self, table, column):
        """
        The table and column are set as part of the Application router, see api/__init__.py
        
        The table corresponds to the cassandra table, while the column specifies the cassandra column to operate on
        The row to operate on is passed to each function, while the value is in the request body, if relevant
        """
        self.table = table
        self.column = column
        self.cass = CassandraClient(self.application.cassandra_factory)
        self.check_columns_exist(settings.CASS_KEYSPACE)

    @defer.inlineCallbacks
    def check_columns_exist(self, keyspace):
        result = yield self.cass.describe_keyspace(keyspace)
        if not result.cf_defs:
            raise Exception( "No column families found in keyspace!")


    @defer.inlineCallbacks
    def get(self, row):
        try:
            result = yield self.cass.get(column_family=self.table, key=row, column=self.column)
            self.finish(result.column.value)
        except NotFoundException, e:
            raise HTTPError(404)
        
    # POST is difficult to generalize as it resource-specific - so force subclasses to implement
    def post(self, *args):
        raise HTTPError(405)

    @defer.inlineCallbacks
    def put(self, row):
        yield self.cass.insert(column_family=self.table, key=row, column=self.column, value=self.request.body)
        self.finish({})

    @defer.inlineCallbacks
    def delete(self, row):
        yield self.cass.remove(column_family=self.table, key=row, column=self.column)
        self.set_status(httplib.NO_CONTENT)
        self.finish()

