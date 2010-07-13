from django.db.backends import *
from django.db.backends.postgresql_psycopg2.base import DatabaseClient
from django.db.backends.postgresql_psycopg2.base import DatabaseCreation
from django.db.backends.postgresql_psycopg2.base import DatabaseIntrospection
from django.db.backends.postgresql_psycopg2.base import DatabaseFeatures
from django.db.backends.postgresql_psycopg2.base import DatabaseOperations
from django.db.backends.postgresql_psycopg2.base import DatabaseWrapper \
    as OriginalDatabaseWrapper
from django.db.backends.postgresql_psycopg2.base import get_version

from django_redis_monitor.cursor_wrapper import MonitoredCursorWrapper

class DatabaseWrapper(OriginalDatabaseWrapper):
    
    def _cursor(self):
        cursor = super(DatabaseWrapper, self)._cursor()
        return MonitoredCursorWrapper(cursor, self)
