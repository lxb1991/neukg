# -*- coding: utf-8 -*-
import engine
import logging


# 获取log的实例
logger = logging.getLogger('pixiu')

mem = {}

mem_count = []

MAX_CACHE = 100


def cache(key, value):

    if len(mem_count) >= MAX_CACHE:

        del_key = mem_count[0]

        logger.info('remove oldest cache:' + del_key)

        del mem_count[0]

        del mem[del_key]

    logger.info('cache key:', key, ';and cache count:', len(mem))

    mem[key] = value

    mem_count.append(key)


def get_cache(key):

    if key in mem:

        logger.info('use cache that key is:', key, ';and cache count:', len(mem))

        return mem[key]

    else:

        return None


def researcher_generate(query):

    cache_name = 'researcher#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        value = engine.get_info_researcher(query)

        if value:

            cache(cache_name, value)

            cache_value = get_cache(cache_name)

        else:

            return None

    return cache_value


def topic_generate(query):

    cache_name = 'topic#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        value = engine.get_info_topic(query)

        if value:

            cache(cache_name, value)

            cache_value = get_cache(cache_name)

        else:

            return None

    return cache_value


def bilingual_generate(query):

    cache_name = 'bilingual#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        value = engine.get_more_bilingual(query)

        if value:

            cache(cache_name, value)

            cache_value = get_cache(cache_name)

        else:

            return None

    return cache_value


def papers_generate(query):

    cache_name = 'papers#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        value = engine.get_more_paper(query)

        if value:

            cache(cache_name, value)

            cache_value = get_cache(cache_name)

        else:

            return None

    return cache_value