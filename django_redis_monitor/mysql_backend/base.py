from django.db.backends import *
from django.db.backends.mysql.base import DatabaseClient
from django.db.backends.mysql.base import DatabaseCreation
from django.db.backends.mysql.base import DatabaseIntrospection
from django.db.backends.mysql.base import DatabaseFeatures
from django.db.backends.mysql.base import DatabaseOperations
from django.db.backends.mysql.base import DatabaseWrapper \
    as OriginalDatabaseWrapper

from django_redis_monitor.cursor_wrapper import MonitoredCursorWrapper

class DatabaseWrapper(OriginalDatabaseWrapper):
    
    def _cursor(self):
        cursor = super(DatabaseWrapper, self)._cursor()
        return MonitoredCursorWrapper(cursor, self)
