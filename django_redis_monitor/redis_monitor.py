import datetime # we use utcnow to insulate against daylight savings errors
import redis

class RedisMonitor(object):
    def __init__(self, prefix='', redis_obj=None, redis_host='localhost', 
            redis_port=6379, redis_db=0
        ):
        assert prefix and ' ' not in prefix, \
            'prefix (e.g. "rps") is required and must not contain spaces'
        self.prefix = prefix
        if redis_obj is None:
            redis_obj = redis.Redis(
                host=redis_host, port=redis_port, db=redis_db
            )
        self.r = redis_obj
    
    def _hash_and_slot(self, dt = None):
        dt = dt or datetime.datetime.utcnow()
        hash = dt.strftime('%Y%m%d:%H') # 20100709:12 = 12th hour of that day
        slot = '%02d:%d' % (  # 24:3 for seconds 30-39 in minute 24
            dt.minute, dt.second / 10
        )
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
        self.r.hincrby(hash, slot + 'w', total_weight)
    
    def get_recent_hits(self, hours = 0, minutes = 0, seconds = 0):
        gathered = self.get_recent_hits_and_weights(hours, minutes, seconds)
        for date, hits, weight in gathered:
            yield date, hits
    
    def get_recent_hits_and_weights(
            self, hours = 0, minutes = 0, seconds = 0
        ):
        start = self._calculate_start(hours, minutes, seconds)
        start = start.replace(
            second = (start.second / 10) * 10, microsecond = 0
        )
        preloaded_hashes = {}
        gathered = []
        current = start
        now = datetime.datetime.utcnow().replace(
            second = (start.second / 10) * 10, microsecond = 0
        )
        while current < now:
            hash, slot = self._hash_and_slot(current)
            if hash not in preloaded_hashes:
                preloaded_hashes[hash] = self.r.hgetall(hash)
            hits = int(preloaded_hashes[hash].get(slot, 0))
            weight = int(preloaded_hashes[hash].get(slot + 'w', 0))
            gathered.append((current, hits, weight))
            current += datetime.timedelta(seconds = 10)
        return gathered
    
    def get_recent_hits_per_second(self, hours = 0, minutes = 0, seconds = 0):
        gathered = self.get_recent_hits(hours, minutes, seconds)
        for date, hits in gathered:
            yield date, hits / 10.0
    
    def get_recent_avg_weights(self, hours = 0, minutes = 0, seconds = 0):
        gathered = self.get_recent_hits_and_weights(hours, minutes, seconds)
        for date, hits, weight in gathered:
            if weight == 0 or hits == 0:
                yield date, 0
            else:
                yield date, float(weight) / hits

class RedisMonitorTotalsOnly(RedisMonitor):
    
    def record_hits_with_total_weight(self, num_hits, total_weight):
        hash = '%s:totals' % self.prefix
        self.r.hincrby(hash, 'hits', num_hits)
        self.r.hincrby(hash, 'weight', total_weight)
    
    def get_recent_hits_and_weights(self, *args, **kwargs):
        raise NotImplemented, 'REDIS_MONITOR_ONLY_TRACK_TOTALS mode'
    
    def get_totals(self):
        hash = '%s:totals' % self.prefix
        return self.r.hgetall(hash) or {}

def get_instance(prefix):
    from django.conf import settings
    from django.core import signals
    host = getattr(settings, 'REDIS_MONITOR_HOST', 'localhost')
    port = getattr(settings, 'REDIS_MONITOR_PORT', 6379)
    db = getattr(settings, 'REDIS_MONITOR_DB', 0)
    only_track_totals = getattr(
        settings, 'REDIS_MONITOR_ONLY_TRACK_TOTALS', False
    )
    if only_track_totals:
        klass = RedisMonitorTotalsOnly
    else:
        klass = RedisMonitor
    obj = klass(prefix, redis_host=host, redis_port=port, redis_db=db)
    # Ensure we disconnect at the end of the request cycle
    signals.request_finished.connect(
        lambda **kwargs: obj.r.connection.disconnect()
    )
    return obj

