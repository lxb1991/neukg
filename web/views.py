# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from DataEngine import memcache, engine, common
from DataEngine.data import CrowdData
import logging


# 获取log的实例
logger = logging.getLogger('pixiu')


def index(request):

    if 'HTTP_X_FORWARDED_FOR' in request.META:

        ip = request.META['HTTP_X_FORWARDED_FOR']

    else:

        ip = request.META['REMOTE_ADDR']

    logger.info("访问的ip： %s"%ip)

    feedback = dict()

    feedback['index'] = True

    return render(request, 'index.html', feedback)


def search(request):

    query = request.POST.get('query_word')

    if query and query.replace(" ", ""):

        query = query.replace(" ", "")

        try:

            feedback = {}

            logger.info("输入的参数：%s" % query)

            # 查看是否有科研人员
            staff = memcache.researcher_generate(query)

            if staff and not staff.is_empty():

                return to_researcher(request, query, staff)

            # 查看是否有概念的信息
            topics = memcache.topic_generate(query)

            if topics and not topics.is_empty():

                return to_topic(request, query, topics)

            feedback['query'] = query

            return render(request, "noresult.html", feedback)

        except UnicodeDecodeError as e:

            logger.error('编码错误', e.message)

            return render(request, "index.html")

    return index(request)


def researcher(request, query):

    query = common.Encrypt.decrypt(query).replace(" ", "")

    if query:

        data = memcache.researcher_generate(query)

        if data and not data.is_empty():

            return to_researcher(request, query, data)

        return render(request, "noresult.html", {'query': query})

    else:

        return index(request)


def topic(request, query):

    query = common.Encrypt.decrypt(query).replace(" ", "")

    if query:

        topics = memcache.topic_generate(query)

        if topics and not topics.is_empty():

            return to_topic(request, query, topics)

        return render(request, "noresult.html", {'query': query})

    else:

        return index(request)


def to_researcher(request, query, data):

    try:

        feedback = {}

        logger.info("to_researcher的参数：%s" % query)

        feedback['query'] = query

        feedback['researcher'] = data

        return render(request, 'researcher.html', feedback)

    except UnicodeDecodeError as e:

        logger.error('编码错误', e.message)

        return index(request)


def to_topic(request, query, topics):

    try:

        feedback = {}

        logger.info("to_topic的参数：%s" % query)

        feedback['query'] = query

        feedback['topics'] = topics

        return render(request, 'topic.html', feedback)

    except UnicodeDecodeError as e:

        logger.error('编码错误', e.message)

        return index(request)


def crowd(request):

    return render(request, "crowddata.html")


def save(request):

    if not request.POST:

        return index(request)

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
