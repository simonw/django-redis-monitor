import datetime # we use utcnow to insulate against daylight savings errors
import redis

class RedisMonitor(object):
    def __init__(self, prefix=''):
        assert prefix and ' ' not in prefix, \
            'prefix (e.g. "rps") is required and must not contain spaces'
        self.prefix = prefix
        self.r = redis.Redis()
    
    def _hash_and_slot(self, dt = None):
        dt = dt or datetime.datetime.utcnow()
        hash = dt.strftime('%Y%m%d:%H') # 20100709:12 = 12th hour of that day
        slot = dt.strftime('%M%S') # 2405 for 5th second of 24th minute
        return ('%s:%s' % (self.prefix, hash), slot)
    
    def _calculate_start(self, hours, minutes, seconds, now = None):
        now = now or datetime.datetime.utcnow()
        delta = (60 * 60 * hours) + (60 * minutes) + seconds
        return now - datetime.timedelta(seconds = delta)
    
    def record_hit(self):
        self.record_hits(1)
    
    def record_hits(self, num_hits):
        hash, slot = self._hash_and_slot()
        self.r.hincrby(hash, slot, num_hits)
    
    def record_hit_with_weight(self, weight):
        self.record_hits_with_total_weight(1, weight)
    
    def record_hits_with_total_weight(self, num_hits, total_weight):
        hash, slot = self._hash_and_slot()
        self.r.hincrby(hash, slot, num_hits)
        self.r.hincrby(hash, slot + 'd', total_weight)
    
    def get_recent_hits_per_second(self, hours = 0, minutes = 0, seconds = 0):
        start = self._calculate_start(hours, minutes, seconds)
    
    def get_recent_avgs_per_second(self, hours = 0, minutes = 0, seconds = 0):
        pass
    
    def get_recent_hits_per_minute(self, hours = 0, minutes = 0, seconds = 0):
        pass
    
    def get_recent_avgs_per_minute(self, hours = 0, minutes = 0, seconds = 0):
        pass
