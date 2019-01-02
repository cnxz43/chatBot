"""chatBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^answer$', views.get_response, name='answer'),
]


# @sched.interval_schedule(seconds=60)

from apscheduler.schedulers.background import BackgroundScheduler
from presses import spider,cennect_redis
sched = BackgroundScheduler()

@sched.scheduled_job(trigger='interval', seconds=60)
def my_task():
    print(spider.update_data())
    print(cennect_redis.publish_alarm())
sched.start()