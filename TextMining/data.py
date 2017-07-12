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
    代表：标题 作者 简介 术语或主题 机构 杂志 域 年代
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


class BiData:
    """ 双语数据 """

    def __init__(self, c_keys, e_keys):

        self.c_keys = c_keys
        self.e_keys = e_keys


class SurveyData:
    """ 综述信息 """

    def __init__(self):

        self.hot_degree = HotDegree()  # 研究热度结果

        self.researcher_list = []
        self.journal_list = []
        self.title_list = []
        self.org_list = []
        self.year_list = []
        self.related_c_topic_list = []
        self.related_e_topic_list = []

        self.year_paps_info = {}  # 按年度分类后的 论文信息
        self.org_paps_info = {}  # 按机构分类后的 论文信息
        self.journal_paps_info = {}  # 按杂志分类后的 论文信息


class AuthorRelationData:
    """ 用户信息关系 """

    def __init__(self, author1, author2, score, flag, ar):

        self.author1 = author1
        self.author2 = author2
        self.score = score
        self.flag = flag
        self.ar = ar


class HotResearchData:
    """ 科研热点 """

    def __init__(self, topic, pap_info, hot_degree):

        self.topic = topic
        self.pap_info = pap_info
        self.hot_degree = hot_degree
        self.hot = hot_degree.hot


class FullOntoData:
    """ 全体本体关系 """

    def __init__(self, onto, occurrence, relation, cf, prob):

        self.onto = onto
        self.occurrence = occurrence
        self.relation = relation
        self.cf = cf
        self.prob = prob


class ThemeData:
    """ 主题信息 """

    def __init__(self, theme, papers):

        self.theme = theme
        self.papers = papers


class HotDegree:
    """ 研究热度 """

    def __init__(self):

        self.hot = 0.0
        self.pap_num = 0  # 论文数目 体现研究热度的信息

        self.recent_3year = ''  # 有论文的最新三年
        self.avg_pap_year = 0.0  # 平均每年论文数
        self.avg_pap_3year = 0.0  # 近三年平均每年论文数

        self.pap_increment_3year = []  # 近三年 论文数量 变化率
        self.person_increment_3year = []  # 近三年 科研人员数 变化率
        self.org_increment_3year = []  # 近三年 研究机构 变化率
        self.journal_increment_3year = []  # 近三年 杂志 论文变化率
        self.key_increment_3year = []  # 近三年 研究点 变化率


class OntologyRelation:
    """ 本体关系 代表这概念之间的关系"""

    def __init__(self):

        self.g_list = []  # 本体之间 全部 关系集合 GeneralRelation

        self.h_list = []  # 本体之间 分类 关系集合 RelationList
        self.e_list = []
        self.s_list = []
        self.i_list = []
        self.m_list = []


class GeneralRelation:
    """ 全部的关系 以及 关系描述 """

    def __init__(self):

        self.tgt_concept = ''
        self.relations = ''
        self.co_occurrence = ''
        self.confidence = 0.0


class RelationList:
    """ 本体之间的关系 E:等价关系  H:层次关系 S:子类关系 M:部分关系 I:实例关系 """

    def __init__(self):

        self.tgt_concept = ''
        self.co_occurrence = ''
        self.confidence = 0.0


class OrgResearchTopic:
    """ 针对某一研究主题的机构统计信息 """

    def __init__(self):

        self.researchers = []
        self.relate_topic = []
        self.journal_list = []
        self.titles = []

        self.paps = []


class JournalResearchTopic:
    """ 针对某一研究主题的杂志统计信息 """

    def __init__(self):

        self.researchers = []
        self.relate_topic = []
        self.org_list = []
        self.titles = []

        self.paps = []


class YearResearchTopic:
    """ 针对某一研究主题的年度统计信息 """

    def __init__(self):

        self.researchers = []  # 记录研究人员列表
        self.relate_topic = []  # 相关研究主题
        self.journal_list = []  # 杂志列表
        self.titles = []  # 论文题目
        self.org_list = []

        self.paps = []


class PaperInfo:
    """ 针对 author 的论文统计信息"""

    def __init__(self):

        self.c_keys = []
        self.e_keys = []
        self.c_journals = []
        self.org = []
        self.years = []
        self.c_titles = []

        self.paps = []


class AuthorRelation:
    """ 作者之间 相似度 描述 """

    def __init__(self):

        self.common_papers = 0  # 相似的信息数目 int
        self.common_c_keys = 0
        self.common_e_keys = 0
        self.common_journal = 0
        self.common_years = 0
        self.common_org = 0

        self.paper_content_sim = 0.0  # 相似度 float

        self.common_papers_sim = 0.0
        self.common_c_keys_sim = 0.0
        self.common_e_keys_sim = 0.0
        self.common_journal_sim = 0.0
        self.common_years_sim = 0.0
        self.common_org_sim = 0.0

        self.final_score = 0.0  # 最终的相似得分


class AuthorPairCommonInfo:
    """ 作者之间 相似内容 描述 """

    def __init__(self):

        self.common_papers = []
        self.common_c_keys = []
        self.common_e_keys = []
        self.common_journals = []
        self.common_years = []
        self.common_org = []


class ARWeight(Const):
    """ 作者关系 相似内容在最后得分的计算权重 """

    C_KEY = 0.2
    E_KEY = 0.00
    JOURNAL = 0.1
    ORG = 0.25
    YEAR = 0.00
    PAPER = 0.3
    CONTENT = 0.15


class ORWeight(Const):
    """ topic 关系的计算权重. ontology relation"""

    OCCURRENCE = 3.0
    HIERARCHY = 3.0
    EQUIVALENCE = 3.0
    SUBCLASS = [50.0, 30.0]
    MERONYMY = [50.0, 20.0]
    INSTANCE = [10.0, 50.0, 10.0, 30.0, 0.3]
    SEM_INTERPRET = []


class ConceptAttribution:
    """ 记录 year 下的论文的属性集合"""

    def __init__(self):

        self.researchers = []
        self.relate_topic = []
        self.org_list = []
        self.titles = []
        self.journals = []


class ConceptAttributionSim:

    def __init__(self):

        self.researchers_sim = 0.0
        self.relate_topic_sim = 0.0
        self.org_list_sim = 0.0
        self.titles_sim = 0.0
        self.journals_sim = 0.0


class CASWeight(Const):
    """ concept attr sim """

    a1 = 0.3
    a2 = 0.4

    f1 = 0.4
    f2 = 0.3
    f3 = 0.3

    tup1 = 0.01
    tup2 = 0.2
    tup3 = 0.1
    tup4 = 0.19
    tup5 = 0.5


class RRWeight(Const):
    """ relation rule"""

    s1 = 3
    s2 = 0.85
    s3 = 0.8
    s4 = 0.3
    s5 = 0.3


class PaperEvaluation:
    """ 论文的价值评价 """

    def __init__(self):

        self.author_value = 0.0
        self.year_value = 0.0
        self.final_value = 0.0

