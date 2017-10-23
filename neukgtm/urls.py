"""neukgtm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Homestartapp nowamagic
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from web import views

urlpatterns = [

    url(r'^index/$', views.index),

    url(r'^search/(?P<query>[^/]*)/$', views.search, name="search"),

    url(r'^researcher/(?P<query>[^/]*)/$', views.researcher, name="researcher"),

    url(r'^topic/(?P<query>[^/]*)/$', views.topic, name="topic"),

    url(r'^crowddata/$', views.crowd),

    url(r'^savedata/$', views.save),

    url(r'^check/$', views.check),

]
