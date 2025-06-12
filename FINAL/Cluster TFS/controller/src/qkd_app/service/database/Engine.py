# Copyright 2022-2024 ETSI SDG TeraFlowSDN (TFS) (https://tfs.etsi.org/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging, sqlalchemy, sqlalchemy_utils
from common.Settings import get_setting

LOGGER = logging.getLogger(__name__)

APP_NAME = 'tfs'
ECHO = False # true: dump SQL commands and transactions executed
CRDB_URI_TEMPLATE = 'cockroachdb://{:s}:{:s}@cockroachdb-public.{:s}.svc.cluster.local:{:s}/{:s}?sslmode={:s}'

class Engine:
    @staticmethod
    def get_engine() -> sqlalchemy.engine.Engine:
        crdb_uri = get_setting('CRDB_URI', default=None)
        if crdb_uri is None:
            CRDB_NAMESPACE = get_setting('CRDB_NAMESPACE')
            CRDB_SQL_PORT  = get_setting('CRDB_SQL_PORT')
            CRDB_DATABASE  = get_setting('CRDB_DATABASE')
            CRDB_USERNAME  = get_setting('CRDB_USERNAME')
            CRDB_PASSWORD  = get_setting('CRDB_PASSWORD')
            CRDB_SSLMODE   = get_setting('CRDB_SSLMODE')
            crdb_uri = CRDB_URI_TEMPLATE.format(
                CRDB_USERNAME, CRDB_PASSWORD, CRDB_NAMESPACE, CRDB_SQL_PORT, CRDB_DATABASE, CRDB_SSLMODE)

        try:
            engine = sqlalchemy.create_engine(
                crdb_uri, connect_args={'application_name': APP_NAME}, echo=ECHO, future=True)
        except: # pylint: disable=bare-except # pragma: no cover
            LOGGER.exception('Failed to connect to database: {:s}'.format(str(crdb_uri)))
            return None

        return engine

    @staticmethod
    def create_database(engine : sqlalchemy.engine.Engine) -> None:
        if not sqlalchemy_utils.database_exists(engine.url):
            sqlalchemy_utils.create_database(engine.url)

    @staticmethod
    def drop_database(engine : sqlalchemy.engine.Engine) -> None:
        if sqlalchemy_utils.database_exists(engine.url):
            sqlalchemy_utils.drop_database(engine.url)
