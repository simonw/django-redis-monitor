from django.db.backends import BaseDatabaseWrapper
from django.conf import settings
from redis_monitor import get_instance
import time, logging

class RedisMonitorMiddleware(object):
    def process_request(self, request):
        if self.should_track_request(request):
            self.tracking = True
            self.start_time = time.time()
            self.rm = get_instance('requests')
        else:
            self.tracking = False
    
    def process_response(self, request, response):
        if getattr(self, 'tracking', False):
            duration = time.time() - self.start_time
            duration_in_microseconds = int(1000000 * duration)
            try:
                self.rm.record_hit_with_weight(duration_in_microseconds)
            except Exception, e:
                logging.warn('RedisMonitor error: %s' % str(e))
        return response
    
    def should_track_request(self, request):
        blacklist = getattr(settings, 'REDIS_MONITOR_REQUEST_BLACKLIST', [])
        for item in blacklist:
            if isinstance(item, basestring) and request.path == item:
                return False
            elif hasattr(item, 'match') and item.match(request.path):
                return False
        return True
