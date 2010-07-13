from django.shortcuts import render_to_response as render
from django.http import HttpResponse
from django.conf import settings
from redis_monitor import get_instance

def monitor(request):
    requests = get_instance('requests')
    sqlops = get_instance('sqlops')
    if getattr(settings, 'REDIS_MONITOR_ONLY_TRACK_TOTALS', False):
        return render('django_redis_monitor/monitor_totals_only.html', {
            'requests': requests.get_totals(),
            'sqlops': sqlops.get_totals(),
        })
    else:
        return render('django_redis_monitor/monitor.html', {
            'requests': reversed(
                list(requests.get_recent_hits_per_second(minutes = 10))
            ),
            'sqlops': reversed(
                list(sqlops.get_recent_hits_per_second(minutes = 10))
            ),
        })

def nagios(request):
    if not getattr(settings, 'REDIS_MONITOR_ONLY_TRACK_TOTALS', False):
        return HttpResponse(
            'nagios only available in REDIS_MONITOR_ONLY_TRACK_TOTALS mode'
        )
    requests = get_instance('requests').get_totals()
    sqlops = get_instance('sqlops').get_totals()
    return render('django_redis_monitor/nagios.xml', {
        'db_count': sqlops.get('hits', 0),
        'db_total_ms': int(int(sqlops.get('weight', 0)) / 1000.0),
        'request_count': requests.get('hits', 0),
        'request_total_ms': int(int(requests.get('weight', 0)) / 1000.0),
    })
