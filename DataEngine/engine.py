# coding=utf-8
from database import DBHandler, SQL
from data import ResearcherData, TopicData
from common import Convert


# --------------------------------------------------------------------
# 单个调用接口。实现模块化的功能

def get_single_bilingual(key):
    """
    获取双语数据
    :param key: 双语词汇
    :return: 对应的双语数据
    """
    return DBHandler.get_single_bi_data(SQL.BI_SINGLE_TOPIC.format(key=key))


def get_researcher(name):
    """
    由 科研人员 获取论文信息
    :param name: 科研人员姓名
    :return: 有数据就返回 paper 信息
    """
    return DBHandler.get_paper_data(SQL.RESEARCHER.format(name=name))


def get_topic(topic):
    """
    由 topic 获取论文信息
    :param topic: 论文关键词
    :return: 有数据就返回 paper 信息
    """
    return DBHandler.get_paper_data(SQL.PAPER.format(topic=topic))


def get_upper_concept(topic):
    """
    获取上位概念
    :param topic: 关键词
    :return: 返回上位概念 OntologyRelation
    """
    return DBHandler.get_relation(SQL.RELATION.format(topic=topic), '1')


def get_lower_concept(topic):
    """
    获取下位概念
    :param topic: 关键词
    :return: 返回下位概念 OntologyRelation
    """
    return DBHandler.get_relation(SQL.RELATION.format(topic=topic), '2')


def get_bilingual(topic):
    """
    获取 双语 more信息
    :param topic: 关键词
    :return: 返回双语列表
    """
    return DBHandler.get_bi_data(SQL.BI_TOPIC.format(topic=topic))


def get_paper(topic):
    """
    获取 paper more信息
    :param topic:
    :return:
    """
    return DBHandler.get_paper_data(SQL.MORE_PAPER.format(topic=topic))


def save_crowd_data(data):
    """
    存储 crowd data 数据到 uncheck 表中
    :param data: crowd data
    :return:
    """
    return DBHandler.save_crowd_data(SQL.SAVE_UNCHECKED.format(author=data.author, org=data.org,
                                                               key=data.key, journal=data.journal))


def get_crowd_data():
    """
    获取 crowd data
    :return:
    """

    return DBHandler.get_crowd_data(SQL.UNCHECKED)

# ---------------------------------------------------------------------
# 汇总的调用接口，给view调用


def get_info_researcher(name):
    """
    获取 科研人员 的格式化信息
    :param name: 科研人员姓名
    :return: ResearcherData
    """
    datas = get_researcher(name=name)

    # 节点容量
    capacity = 10

    if len(datas):

        researcher_data = ResearcherData()

        for data in datas:

            # 添加机构信息：
            Convert.str2list(data.c_org, researcher_data.organizations, capacity)

            # 添加研究主题：
            Convert.str2list(data.c_keys, researcher_data.topics, capacity)

            # 添加相关人员信息：
            Convert.str2list(data.c_authors, researcher_data.researchers, capacity)

            # 添加机构信息：
            Convert.str2list(data.c_journal, researcher_data.journals, capacity)

        # 删除自身在相关人员中
        if name in researcher_data.researchers:

            researcher_data.researchers.remove(name)

        # 对机构长短进行排序
        researcher_data.organizations.sort(key=lambda x: len(x))

        return researcher_data

    else:

        return None


def get_info_topic(topic):
    """
    获取 概念 的格式化信息
    :param topic: 概念名称
    :return: TopicData
    """

    datas = get_topic(topic)

    if len(datas):

        capacity = 10

        topic_data = TopicData()

        cn_key, en_key = get_single_bilingual(key=topic)

        if cn_key and en_key:

            topic_data.bilinguals.bi_cn = cn_key

            topic_data.bilinguals.bi_en = en_key

        for data in datas:

            if data.e_keys and data.c_keys:

                Convert.str2list(data.c_keys, topic_data.bilingual_cn, capacity)

                Convert.str2list(data.e_keys, topic_data.bilingual_en, capacity)

        # 获取上下位概念

        upper = get_upper_concept(topic=topic)

        lower = get_lower_concept(topic=topic)

        for general_concept in upper.g_list:

            topic_data.topics_upper.append(general_concept.tgt_concept)

        for general_concept in lower.g_list:

            topic_data.topics_lower.append(general_concept.tgt_concept)

        topic_data.concept = get_relation_describe(topic=topic, upper_relations=upper.g_list,
                                                   lower_relations=lower.g_list)

        return topic_data

    else:

        return None


def get_more_bilingual(topic):
    """
    获取更多的双语信息
    :param topic: 关键词
    :return: 双语列表 list[BiData]
    """
    bis = get_bilingual(topic=topic)

    if len(bis):

        return bis

    else:

        return None


def get_more_paper(topic):
    """
    获取更多的paper信息
    :param topic: 关键词
    :return: paper列表 list[paper]
    """
    papers = get_paper(topic)

    if len(papers):

        return papers

    else:

        return None


def save_unchecked_paper(data):
    """
    存储 未通过人工审核的数据
    :param paper: CrowdData
    :return: 操作成功与否 True False
    """

    save_crowd_data(data)

# -----------------------------------------------------------------------------
# 内部调用函数


def get_relation_describe(topic, upper_relations, lower_relations):
    """ 获取关系描述 """

    relation_desc = ''

    dot_mark = 0  # 是否需要加顿号 需要则说明有多个概念

    for i in range(len(upper_relations)):

        if not i:

            relation_desc += topic + '概念是：' + upper_relations[i].tgt_concept

        else:

            relation_desc += '、' + upper_relations[i].tgt_concept

        dot_mark += 1

    if dot_mark and len(upper_relations):

        relation_desc += "等概念下的研究内容，"

    for i in range(len(lower_relations)):

        if not i and not dot_mark:

            relation_desc += topic + '概念是：' + lower_relations[i].tgt_concept

        elif not i and dot_mark:

            relation_desc += '同时' + topic + '又包括：' + lower_relations[i].tgt_concept

        else:

            relation_desc += '、' + lower_relations[i].tgt_concept

        dot_mark += 1

    if dot_mark and len(lower_relations):

        relation_desc += '等研究内容。\n'

    return relation_desc
