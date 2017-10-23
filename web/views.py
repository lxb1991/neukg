# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from DataEngine import memcache, engine
from DataEngine.data import CrowdData
import logging


# 获取log的实例
logger = logging.getLogger('pixiu')


def index(request):

    return render(request, 'index.html')


def search(request, query):

    feedback = {}

    logger.info("输入的参数：%s" % query)

    # 查看是否有科研人员
    staff = memcache.researcher_generate(query)

    if staff:

        return to_researcher(request, query, staff)

    # 查看是否有概念的信息
    topics = memcache.topic_generate(query)

    if topics:

        return to_topic(request, query, topics)

    feedback['query'] = query

    return render(request, "noresult.html", feedback)


def researcher(request, query):

    data = memcache.researcher_generate(query)

    return to_researcher(request, query, data)


def topic(request, query):

    topics = memcache.topic_generate(query)

    return to_topic(request, query, topics)


def to_researcher(request, query, data):

    feedback = {}

    logger.info("输入的参数：%s" % query)

    feedback['query'] = query

    feedback['researcher'] = data

    return render(request, 'researcher.html', feedback)


def to_topic(request, query, topics):

    feedback = {}

    logger.info("输入的参数：%s" % query)

    feedback['query'] = query

    feedback['topics'] = topics

    return render(request, 'topic.html', feedback)


def crowd(request):

    return render(request, "crowddata.html")


def save(request):

    if not request.POST:

        return render(request, "index.html")

    feedback = {}

    data = CrowdData()

    author = request.POST.get("author")

    org = request.POST.get("org")

    key = request.POST.get("key")

    journal = request.POST.get("journal")

    if author and key and org and journal:

        data.author = author

        data.key = key

        data.org = org

        data.journal = journal

        engine.save_unchecked_paper(data)

        return render(request, "success.html")

    feedback["author"] = author

    feedback["org"] = org

    feedback["key"] = key

    feedback["journal"] = journal

    feedback["error"] = "请完整、正确的填写要求的数据"

    return render(request, "crowddata.html", feedback)


def check(request):

    feedback = {}

    if request.POST:

        pwd = request.POST.get("password")

        if pwd == 'neukg':

            feedback['login'] = True

            feedback['datas'] = engine.get_crowd_data()

        else:

            feedback["error"] = "密码错误！！！"

    return render(request, "check.html", feedback)
