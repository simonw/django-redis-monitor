import time

def monkeypatched_cursor_method(self):
    cursor = self.cursor_original()
    return MonitoredCursorWrapper(cursor, self)

class MonitoredCursorWrapper(object):
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    def execute(self, sql, params=()):
        start = time.time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = time.time()
            sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            print "%.0f : %s" % (1000000 * (stop - start), sql)
    
    def executemany(self, sql, param_list):
        start = time.time()
        try:
            return self.cursor.executemany(sql, param_list)
        finally:
            stop = time.time()
            print "%.0f : %d * %s" % (
                1000000 * (stop - start), len(param_list), sql
            )
    
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)
    
    def __iter__(self):
        return iter(self.cursor)
