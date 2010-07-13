from django.shortcuts import render_to_response as render
from redis_monitor import get_instance

def monitor(request):
    requests = get_instance('requests')
    sqlops = get_instance('sqlops')
    return render('django_redis_monitor/monitor.html', {
        'requests': reversed(
            list(requests.get_recent_hits_per_second(minutes = 10))
        ),
        'sqlops': reversed(
            list(sqlops.get_recent_hits_per_second(minutes = 10))
        ),
    })
