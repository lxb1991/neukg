# coding=utf-8

# --------------------------------------------------------------------
#  用到的数据对象


class Const(object):
    """
    const 类. 变量赋值后不可改变
    """
    def __setattr__(self, key, value):

        if key in self.__dict__:

            raise(self.ConstError, 'Const变量 不可赋值')
        else:

            self.__dict__[key] = value

    class ConstError(TypeError):
        pass


class PaperData:
    """
    代表数据库 computer 中 paper 数据类型
    代表：标题 作者 简介 术语或主题 机构 杂志 doi 年代
    """

    def __init__(self, c_title, e_title, c_authors, e_authors, c_abs, e_abs,
                 c_keys, e_keys, c_org, e_org, c_journal, e_journal, doi, year):

        self.c_title = c_title
        self.e_title = e_title

        self.c_authors = c_authors
        self.e_authors = e_authors

        self.c_abs = c_abs
        self.e_abs = e_abs

        self.c_keys = c_keys
        self.e_keys = e_keys

        self.c_org = c_org
        self.e_org = e_org

        self.c_journal = c_journal
        self.e_journal = e_journal

        self.doi = doi

        self.year = year


class ResearcherData:
    """ 研究人员的数据 """

    def __init__(self):

        self.organizations = []

        self.topics = []

        self.researchers = []

        self.journals = []


class TopicData:
    """ 概念信息数据 """

    def __init__(self):

        self.bilinguals = BiData()

        self.bilingual_cn = []

        self.bilingual_en = []

        self.topics_upper = []

        self.topics_lower = []

        self.concept = ""


class OntologyRelation:
    """ 本体关系 代表这概念之间的关系"""

    def __init__(self):

        self.g_list = []  # 本体之间 全部 关系集合 GeneralRelation

        self.h_list = []  # 本体之间 分类 关系集合 RelationList
        self.e_list = []
        self.s_list = []
        self.i_list = []
        self.m_list = []


class RelationList:
    """ 本体之间的关系 E:等价关系  H:层次关系 S:子类关系 M:部分关系 I:实例关系 """

    def __init__(self):

        self.tgt_concept = ''


class GeneralRelation:
    """ 全部的关系 以及 关系描述 """

    def __init__(self):

        self.tgt_concept = ''
        self.relations = ''


class BiData:
    """ 双语数据"""

    def __init__(self):

        self.bi_cn = ""

        self.bi_en = ""


class CrowdData:
    """ 众筹数据"""

    def __init__(self):

        self.author = ""

        self.org = ""

        self.journal = ""

        self.key = ""
