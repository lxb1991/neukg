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
from django.contrib import admin
from web import views

urlpatterns = [

    url(r'^admin/', admin.site.urls),

    url(r'^index/$', views.index),

    url(r'^query_msg/$', views.query_msg, {'control': '0', 'query': '', 'page': '0'}),

    url(r'^query_msg/(?P<control>[0-9]*)/(?P<query>[^/]*)/(?P<page>[0-9]*)', views.query_msg),

    url(r'^survey/$', views.survey),

    url(r'^hot_research/$', views.hot_research, {'page': '0'}),

    url(r'^hot_research/(?P<page>[0-9]*)', views.hot_research),

    url(r'^relation/$', views.relation, {'query': '', 'page': '0'}),

    url(r'^relation/(?P<query>[^/]*)/(?P<page>[0-9]*)', views.relation),

    url(r'^ontology/$', views.ontology, {'page': '0'}),

    url(r'^ontology/(?P<page>[0-9]*)', views.ontology),

    url(r'^ontology_relation/$', views.ontology_relation, {'page': '0'}),

    url(r'^ontology_relation/(?P<page>[0-9]*)', views.ontology_relation),

    url(r'^researcher/$', views.researcher),

    url(r'^cluster/$', views.cluster),

]
