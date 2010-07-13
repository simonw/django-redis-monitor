from django.db.backends import BaseDatabaseWrapper
from redis_monitor import get_instance
import time, logging

class RedisMonitorMiddleware(object):
    def process_request(self, request):
        self.start_time = time.time()
        self.rm = get_instance('requests')
    
    def process_response(self, request, response):
        duration = time.time() - self.start_time
        duration_in_microseconds = int(1000000 * duration)
        try:
            self.rm.record_hit_with_weight(duration_in_microseconds)
        except Exception, e:
            logging.warn('RedisMonitor error: %s' % str(e))
        return response
