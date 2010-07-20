django-redis-monitor
====================

Redis-backed performance monitoring for Django. Can keep track of Django 
requests per second, Django SQL operations per second and the average 
duration per request or per SQL operation over time.

Numbers of hits and overall weights are stored in 10 second buckets, to save 
on space. Only results from previous complete buckets are returned, so it can 
take up to 10 seconds for a hit to be registered in the hits-per-second 
metrics.

Installation:
-------------

You will need to install and run a Redis server using a recent version of 
Redis (one that supports the HINCRBY and HGETALL commands). Redis 2.0.0 or 
higher should be fine.

You will also need redis-py from http://github.com/andymccurdy/redis-py/ - 
you can pip install the latest version like so:

    pip install http://github.com/andymccurdy/redis-py/tarball/master

Usage:
------

1. Ensure django_redis_monitor is on your Python path.

2. Add RedisMonitorMiddleware to your middleware, at the top of the stack 
   so that the performance overhead added by other middlewares is included 
   in the request duration calculation:

    MIDDLEWARE_CLASSES = (
        'django_redis_monitor.middleware.RedisMonitorMiddleware',
    ) + MIDDLEWARE_CLASSES

3. Set your DATABASE_ENGINE setting to 'django_redis_monitor.sqlite3_backend'
   or 'django_redis_monitor.postgresql_psycopg2_backend' or 
   'django_redis_monitor.mysql_backend' so your SQL queries can be 
   intercepted and counted.
   
   If you are using South for migrations, you will also need to add a 
   corresponding SOUTH_DATABASE_ADAPTERS setting:
   
   SOUTH_DATABASE_ADAPTERS = {
       'default': 'south.db.postgresql_psycopg2',
                  # Or 'south.db.sqlite3' or 'south.db.mysql'
   }

4. Optional step: Add redis settings to your settings.py file (otherwise 
   the following defaults will be used):

    REDIS_MONITOR_HOST = 'localhost'
    REDIS_MONITOR_PORT = 6379
    REDIS_MONITOR_DB = 0

5. Add 'django_redis_monitor' to your INSTALLED_APPS setting so Django can 
   find the correct template for the monitor view. Alternatively, copy the 
   monitor.html template in to a django_redis_monitor directory in your 
   existing templates/ directory.

7. By default, django_redis_monitor records statistics over time in to 
   separate buckets. If you are using an external monitoring tool such as 
   Nagios you may only need to report the total number or duration of requests
   since counting began. If so, you can add the following setting:
   
   REDIS_MONITOR_ONLY_TRACK_TOTALS = True

8. Hook up the monitoring view function in your urls.py:

    urlpatterns = patterns('',
        # ...
        (r'^redis-monitor/$', 'django_redis_monitor.views.monitor'),
    )
    
    If you plan to use the nagios reporting hook, add this as well:
    
        (r'^redis-monitor/nagios\.xml$', 'django_redis_monitor.views.nagios'),
    
If you want the monitoring view to only be visible to super users, do this:

    from django_redis_monitor.views import monitor
    from django.contrib.auth.decorators import user_passes_test
    
    def requires_superuser(view_fn):
        decorator = user_passes_test(lambda u: u.is_superuser)
        return decorator(view_fn)
    
    urlpatterns = patterns('',
        # ...
        ('^redis-monitor/$', requires_superuser(monitor)),
    )

9. Hit your application with a bunch of requests.

10. Go to http://localhost:8000/redis-monitor/ to see the results.
