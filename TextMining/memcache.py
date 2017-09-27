# -*- coding: utf-8 -*-
import mine


mem = {}

mem_count = []

MAX_CACHE = 30


def cache(key, value):

    if len(mem_count) >= MAX_CACHE:

        del_key = mem_count[0]

        print('remove oldest cache:' + del_key)

        del mem_count[0]

        del mem[del_key]

    print('cache key:', key, ';and cache count:', len(mem))

    mem[key] = value

    mem_count.append(key)


def get_cache(key):

    if key in mem:

        print('use cache that key is:', key, ';and cache count:', len(mem))

        return mem[key]

    else:

        return None


def msg_keys_generate(query):

    cache_name = 'bi#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_bi_key(query))

        cache_value = get_cache(cache_name)

    return cache_value


def msg_title_generate(query):

    cache_name = 'title#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_bi_title(query))

        cache_value = get_cache(cache_name)

    return cache_value


def msg_full_generate(query):

    cache_name = 'full#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_paper_data(query))

        cache_value = get_cache(cache_name)

    return cache_value


def hot_research_generate():

    cache_name = 'hot#'

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_hot_research())

        cache_value = get_cache(cache_name)

    return cache_value


def author_relation_generate(query):

    cache_name = 'ar#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_author_relation(query))

        cache_value = get_cache(cache_name)

    return cache_value


def ontology_generate():

    cache_name = 't_onto#'

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_topic_ontology())

        cache_value = get_cache(cache_name)

    return cache_value


def ontology_relation_generate():

    cache_name = 'full_onto#'

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.get_full_ontology())

        cache_value = get_cache(cache_name)

    return cache_value


def cluster(query):

    cache_name = 'cluster#' + query

    cache_value = get_cache(cache_name)

    if not cache_value:

        cache(cache_name, mine.divide_topic(query))

        cache_value = get_cache(cache_name)

    return cache_value
