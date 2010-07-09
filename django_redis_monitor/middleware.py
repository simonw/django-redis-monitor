from django.db.backends import BaseDatabaseWrapper
from cursor_wrapper import monkeypatched_cursor_method
import time

class RedisMonitorMiddleware(object):
    def process_request(self, request):
        self.ensure_monkeypatch()
        self.start_time = time.time()
    
    def process_response(self, request, response):
        duration = time.time() - self.start_time
        print "Request duration: %.0f" % (1000000 * duration)
        return response
    
    def ensure_monkeypatch(self):
        if BaseDatabaseWrapper.cursor != monkeypatched_cursor_method:
            BaseDatabaseWrapper.cursor_original = BaseDatabaseWrapper.cursor
            BaseDatabaseWrapper.cursor = monkeypatched_cursor_method
