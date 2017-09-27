# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from TextMining import memcache, mine


def index(request):

    return render(request, 'index.html')


def query_msg(request, control, query, page):

    feedback = {}

    try:

        if request.POST.get('query_word'):

            query = request.POST.get('query_word')

        if request.POST.get('control'):

            control = request.POST.get('control')

        page = int(page) if int(page) > 1 else 1

        if query.strip():  # 判断是否返回数据 依据就是 query 是否为空

            if control == '1':

                result = memcache.msg_keys_generate(query)

            elif control == '2':

                result = memcache.msg_title_generate(query)

            else:

                result = memcache.msg_full_generate(query)

            # 需要传递到view的数据
            feedback['count'] = len(result)

            feedback['control'] = control

            feedback['query'] = query

            feedback['results'], feedback['pages'] = pagination(result, page)

    except Exception as e:

        print(e.message)

        feedback['error'] = "你的请求url可能有问题，请点击热点预测按钮发起请求。请再试一试！"

        return render(request, '500.html', feedback)

    return render(request, 'query_msg.html', feedback)


def survey(request):
    """ 生成综述信息 """

    feedback = {}

    if request.method == 'POST' and request.POST.get('query_word').strip():

        query = request.POST.get('query_word').strip()

        try:

            feedback['survey'], feedback['upper'], feedback['lower'], feedback['desc'] = mine.get_survey(query)

        except BaseException as e:

            print(e.message)

            feedback['error'] = "你的输入的方向，好像没有人有研究。请换一个关键字再试一试！"

            return render(request, '500.html', feedback)

    return render(request, 'survey.html', feedback)


def hot_research(request, page):
    """ 热点查询 """

    feedback = {}

    if page != '0':

        try:

            page = int(page)

            results = memcache.hot_research_generate()

            feedback['count'] = len(results)

            feedback['results'], feedback['pages'] = pagination(results, page)

        except Exception as e:

            print(e.message)

            feedback['error'] = "你的请求url可能有问题，请点击热点预测按钮发起请求。请再试一试！"

            return render(request, '500.html', feedback)

    return render(request, 'hot_research.html', feedback)


def relation(request, query, page):
    """ 用户关系查询"""

    feedback = {}

    if not query:

        query = request.POST.get('query_word')

    if page != '0':

            page = int(page)

            print(query, page)

            results = memcache.author_relation_generate(query)

            feedback['query'] = query

            feedback['count'] = len(results)

            feedback['results'], feedback['pages'] = pagination(results, page)

    return render(request, 'relation.html', feedback)


def ontology(request, page):

    feedback = {}

    if page != '0':

        page = int(page)

        results = memcache.ontology_generate()

        feedback['count'] = len(results)

        feedback['results'], feedback['pages'] = pagination(results, page)

    return render(request, 'ontology.html', feedback)


def ontology_relation(request, page):

    feedback = {}

    if page != '0':

        page = int(page)

        results = memcache.ontology_relation_generate()

        feedback['count'] = len(results)

        feedback['results'], feedback['pages'] = pagination(results, page)

    return render(request, 'ontology_relation.html', feedback)


def cluster(request):

    feedback = {}

    if request.method == 'POST' and request.POST.get('query_word').strip():

        query = request.POST.get('query_word').strip()

        feedback['results'] = memcache.cluster(query)

    return render(request, 'cluster.html', feedback)


def researcher(request):
    """ 科研人员信息查询 """

    feedback = {}

    if request.method == 'POST' and request.POST.get('query_word').strip():

        query = request.POST.get('query_word').strip()

        feedback['query'] = query

        try:

            feedback['survey'] = mine.get_researcher(query)

        except BaseException as e:

            print(e.message)

            feedback['error'] = "你的输入的研究人员，查无此人。请换一个研究人再试一试！"

            return render(request, '500.html', feedback)

    return render(request, 'researcher.html', feedback)


def pagination(result, page):
    """ 为了实现分页功能 传递的方法：result 是传人需要分页的数据， page 是当前页"""

    paginator = Paginator(result, 50)  # 默认每页有50条数据。

    try:
        result = paginator.page(page)

    except PageNotAnInteger:

        # If page is not an integer, deliver first page.
        result = paginator.page(1)

    except EmptyPage:

        # If page is out of range (e.g. 9999), deliver last page of results.
        result = paginator.page(paginator.num_pages)

    if len(paginator.page_range) > 4:

        if result.number > 3:

            first = result.number - 2

        else:

            first = 1

        if paginator.num_pages - result.number > 3:

            last = result.number + 2

        else:

            last = paginator.num_pages

        if last - first < 4:

            if first == 1:

                last = first + 4
            else:

                first = last - 4

        pages = range(first, last + 1)

    else:

        pages = paginator.page_range

    return result, pages
