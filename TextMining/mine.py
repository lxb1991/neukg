# coding=utf-8
from data import SurveyData, HotDegree, AuthorRelation, AuthorPairCommonInfo, ConceptAttribution, ConceptAttributionSim,\
    AuthorRelationData, HotResearchData, FullOntoData, ARWeight, ORWeight, CASWeight, RRWeight
from database import DBHandler, SQL
from kmeans import KMeans
from common import Convert, Graph
import re

# --------------------------------------------------------------------
# mine 作为调用接口，可供调用的函数。


def get_bi_key(topic):
    """
    获取双语术语. 数据库 computer表 的 c_keys 和 e_keys 字段
    tip: 为了和字典中 key 区别我们使用 topic 来代表 c_keys 的关键字
    :return [BiData, ] 返回BiData的列表
    """
    return DBHandler.get_bi_data(SQL.BI_TOPIC.format(topic=topic))


def get_bi_title(title):
    """
    获取双语标题. 数据库 computer表 的 c_title 和 e_title 字段
    :return [BiData, ] 返回BiData的列表
    """
    return DBHandler.get_bi_data(SQL.BI_TITLE.format(title=title))


def get_paper_data(topic):
    """
    查找全部信息. 数据库 computer表 的全部字段
    :return [PaperData, ] 返回PaperData的列表
    """

    return DBHandler.get_paper_data(SQL.PAPER.format(topic=topic))


def get_survey(topic):
    """
    生成关于 topic 的综述信息
    :return (survey, upper, lower, survey_desc)
    返回 survey 综述信息SurveyData
        upper 上位概念OntologyRelation
        lower 下位概念 OntologyRelation
        survey_desc 综述主题描述信息
    """
    paper_data = DBHandler.get_paper_data(SQL.SURVEY.format(topic=topic))

    generator = SurveyGenerator(topic=topic, papers=paper_data)

    generator.generate_chn_survey()

    return generator.survey, generator.upper, generator.lower, generator.concept_desc


def get_researcher(author):
    """
    科研人员分析
    :return  survey  返回研究人员的SurveyData 信息
    """

    paper_data = DBHandler.get_paper_data(SQL.RESEARCHER.format(author=author))

    generator = ResearchGenerator(author=author, papers=paper_data)

    generator.generate_researcher()

    return generator.researcher_survey_info


def get_author_relation(topic):
    """
    用户关系挖掘
    :return [AuthorRelationData, ] 返回 AuthorRelationData 列表
    """

    paper_data = DBHandler.get_paper_data(SQL.AUTHOR_RELATION.format(topic=topic))

    generator = AuthorGenerator(papers=paper_data)

    generator.generate_author_relation()

    return generator.author_relations


def get_hot_research():
    """
    科研热点预测
    :return [HotResearchData, ]  返回 HotResearchData 列表
    """

    paper_data = DBHandler.get_paper_data(SQL.HOT_RESEARCH)

    generator = HotResearchGenerator(papers=paper_data)

    generator.generate_hot_research()

    generator.hot_researches.sort(key=lambda h: h.hot, reverse=True)

    return generator.hot_researches


def get_topic_ontology():
    """
    获取亚本体信息 即 topic
    :return {topic-topic: prob_score, }
    """

    topics = DBHandler.get_keys(SQL.ONTOLOGY)

    generator = TopicOntologyGenerator(topics=topics)

    generator.generate_topic_ontology()

    return sorted(generator.prob_edge.items(), key=lambda x, y: cmp(x[1], y[1]))


def get_full_ontology():
    """
    全体关系生成
    """

    topics = DBHandler.get_keys(SQL.ONTOLOGY)

    generator = TopicOntologyGenerator(topics=topics)

    generator.generate_full_ontology()

    return generator.results


def get_year_ontology_unsupervised(topic):
    """
    无监督 时间 本体抽取
    """

    paper_data = DBHandler.get_paper_data(SQL.ONTOLOGY_UNSUPERVISED.format(topic=topic))

    generator = YearOntologyGenerator(paper_data)

    generator.generate_year_ontology()


def get_equal_relation():
    """
    获取等价关系
    """

    topics = DBHandler.get_keys(SQL.ONTOLOGY)

    generator = TopicOntologyGenerator(topics=topics)

    generator.generate_equal_relation()


def divide_topic(topic):
    """
    主题词聚类
    :return [ThemeData, ] 返回 ThemeData 主题聚类列表
    """

    paper_data = DBHandler.get_paper_data(SQL.TOPIC.format(topic=topic))

    generator = KMeans(papers=paper_data)

    generator.generate_themes()

    return generator.themes

# --------------------------------------------------------------------
#  生成数据的类


class SurveyGenerator(object):
    """ 综述生成类 """

    def __init__(self, topic, papers):

        if not topic or not papers or not len(papers):

            raise(BaseException, '参数不能为空')

        self.topic = topic

        self.papers = papers

        self.upper = None   # 需要返回的信息 上位概念：比如 机器翻译 是 人工智能 的子概念。那么人工智能就是上位概念！

        self.lower = None

        self.survey = None

        self.concept_desc = None

    def generate_chn_survey(self):
        """ 中文综述生成 """

        self.upper = DBHandler.get_relation(SQL.RELATION.format(topic=self.topic), '1')  # 获取上位关系和下位关系

        self.lower = DBHandler.get_relation(SQL.RELATION.format(topic=self.topic), '2')

        self.__generate_concept_describe()

        self.generate_chn_survey_info()

    def __generate_concept_describe(self):
        """ 综述内容的概念描述 """

        e_str = self.__get_relation_describe(self.upper.e_list, self.lower.e_list, "等价")

        i_str = self.__get_relation_describe(self.upper.i_list, self.lower.i_list, "实例")

        m_str = self.__get_relation_describe(self.upper.m_list, self.lower.m_list, "部分整体")

        s_str = self.__get_relation_describe(self.upper.s_list, self.lower.s_list, "子类")

        h_str = self.__get_relation_describe(self.upper.h_list, self.lower.h_list, "层次")

        self.concept_desc = e_str + i_str + m_str + s_str + h_str

    def __get_relation_describe(self, upper_relations, lower_relations, r_type):
        """ 获取各个类别 r_type 的关系描述 """

        relation_desc = ''

        dot_mark = 0  # 是否需要加顿号 需要则说明有多个概念

        if r_type == "层次":

            for i in range(len(upper_relations)):

                if not i:

                    relation_desc += self.topic + '是' + upper_relations[i].tgt_concept

                else:

                    relation_desc += '、' + upper_relations[i].tgt_concept

                dot_mark += 1

            if dot_mark:

                relation_desc += '等研究主题下的一个研究方向；'

            for i in range(len(lower_relations)):

                if not i and not dot_mark:

                    relation_desc += self.topic + '有' + lower_relations[i].tgt_concept

                elif not i and dot_mark:

                    relation_desc += '\n同时' + self.topic + '也有' + lower_relations[i].tgt_concept

                else:

                    relation_desc += '、' + lower_relations[i].tgt_concept

                dot_mark += 1

            if dot_mark and len(lower_relations):

                relation_desc += '等研究内容；\n'

            return relation_desc

        for i in range(len(upper_relations)):

            if not i:

                relation_desc += self.topic + '是一个以自己为终点，并与上位概念：' + upper_relations[i].tgt_concept

            else:

                relation_desc += '、' + upper_relations[i].tgt_concept

            dot_mark += 1

        if dot_mark:

            relation_desc += '等有' + r_type + '关系的概念\n'

        for i in range(len(lower_relations)):

            if not i and not dot_mark:

                relation_desc += self.topic + '是一个以自己为起点，并与下位概念：' + lower_relations[i].tgt_concept

            elif not i and dot_mark:

                relation_desc += '同时' + self.topic + '也是一个以自己为起点，并与下位概念：' + lower_relations[i].tgt_concept

            else:

                relation_desc += '、' + lower_relations[i].tgt_concept

            dot_mark += 1

        if dot_mark and len(lower_relations):

            relation_desc += '等有' + r_type + '关系的概念；\n'

        return relation_desc

    def generate_chn_survey_info(self):
        """ 得到中文综述 survey 对象, 主要就是填充 survey 对象"""

        self.survey = SurveyData()

        for paper in self.papers:
            # 把 paper 的信息注入到 survey 中

            Convert.paper2other(paper.c_journal, self.survey.journal_list)
            Convert.paper2other(paper.c_org, self.survey.org_list)
            Convert.paper2other(paper.c_authors, self.survey.researcher_list)
            Convert.paper2other(paper.c_title, self.survey.title_list)
            Convert.paper2other(paper.year, self.survey.year_list)
            Convert.paper2other(paper.c_keys, self.survey.related_c_topic_list)
            Convert.paper2other(paper.e_keys, self.survey.related_e_topic_list)

            Convert.paper2journal_paps(paper, self.survey.journal_paps_info)
            Convert.paper2org_paps(paper, self.survey.org_paps_info)
            Convert.paper2year_paps(paper, self.survey.year_paps_info)

        del self.papers  # 清空 paper 集合

        self.survey.topic = self.topic

        self.survey.hot_degree.pap_num = len(self.survey.title_list)  # 热点论文数目

        temp_hot = Convert.generate_hot_degree(self.survey.hot_degree, self.survey.year_paps_info)

        self.survey.hot_degree.hot = Convert.calculate_hot_degree_by_survey(self.survey, temp_hot)


class ResearchGenerator(object):
    """ 生成科研人员信息 """

    def __init__(self, author, papers):

        if not author or not papers or not len(papers):

            raise(BaseException, '参数不能为空')

        self.author = author

        self.papers = papers

        self.researcher_survey_info = None

    def generate_researcher(self):

        survey = SurveyGenerator(self.author, self.papers)

        survey.generate_chn_survey_info()

        self.researcher_survey_info = survey.survey


class AuthorGenerator(object):

    def __init__(self, papers):

        if not papers or not len(papers):

            raise(BaseException, '参数不能为空')

        self.papers = papers

        self.author_paps = {}

        self.author_relations = []

    def generate_author_relation(self):

        Convert.paper2author_paps(self.papers, self.author_paps)

        print('数据转化完毕 删除papers。。。')

        del self.papers

        self.__calculate_author_relation()

    def __calculate_author_relation(self):
        """ 计算作者关系相似度 """

        stop_words = Convert.get_stop_word()

        authors = self.author_paps.keys()

        for author_1 in authors:

            pap_info_1 = self.author_paps[author_1]

            if not author_1 or not len(author_1) or not pap_info_1:

                continue

            for author_2 in authors:

                pap_info_2 = self.author_paps[author_2]

                if not author_2 or not len(author_2) or not pap_info_2 or author_1 == author_2:

                    continue

                ar = AuthorRelation()  # 相似度 float

                ar_common = AuthorPairCommonInfo()  # 相似内容 str

                # 计算不同作者的 属性 内容相似数目
                ar.common_c_keys = AuthorGenerator.get_author_relation_common(pap_info_1.c_keys, pap_info_2.c_keys, ar_common.common_c_keys)
                ar.common_e_keys = AuthorGenerator.get_author_relation_common(pap_info_1.e_keys, pap_info_2.e_keys, ar_common.common_e_keys)
                ar.common_journal = AuthorGenerator.get_author_relation_common(pap_info_1.c_journals, pap_info_2.c_journals, ar_common.common_journals)
                ar.common_org = AuthorGenerator.get_author_relation_common(pap_info_1.org, pap_info_2.org, ar_common.common_org)
                ar.common_years = AuthorGenerator.get_author_relation_common(pap_info_1.years, pap_info_2.years, ar_common.common_years)
                ar.common_papers = AuthorGenerator.get_author_relation_common(pap_info_1.c_titles, pap_info_2.c_titles, ar_common.common_papers)
                # 计算不同作者的 论文 内容相似度
                ar.paper_content_sim = AuthorGenerator.calculate_paper_sim(pap_info_1.paps, pap_info_2.paps, stop_words)

                # 计算不同作者的 属性 内容相似度 = 相似内容数目 * 2 ／ 内容数目之和
                # eg. [机器学习;自然语言处理][机器学习;神经网络] 相似度 = 1 * 2 ／ 4 = 0.5
                if len(pap_info_1.c_keys) + len(pap_info_2.c_keys):

                    ar.common_c_keys_sim = float(ar.common_c_keys) * 2 / (len(pap_info_1.c_keys) + len(pap_info_2.c_keys))

                if len(pap_info_1.e_keys) + len(pap_info_2.e_keys):

                    ar.common_e_keys_sim = float(ar.common_e_keys) * 2 / (len(pap_info_1.e_keys) + len(pap_info_2.e_keys))

                if len(pap_info_1.c_journals) + len(pap_info_2.c_journals):

                    ar.common_journal_sim = float(ar.common_journal) * 2 / (len(pap_info_1.c_journals) + len(pap_info_2.c_journals))

                if len(pap_info_1.org) + len(pap_info_2.org):

                    ar.common_org_sim = float(ar.common_org) * 2 / (len(pap_info_1.org) + len(pap_info_2.org))

                if len(pap_info_1.c_titles) + len(pap_info_2.c_titles):

                    ar.common_papers_sim = float(ar.common_papers) * 2 / (len(pap_info_1.c_titles) + len(pap_info_2.c_titles))

                if len(pap_info_1.years) + len(pap_info_2.years) > 0:

                    ar.common_years_sim = float(ar.common_years) * 2 / (len(pap_info_1.years) + len(pap_info_2.years))

                ar.final_score = ar.paper_content_sim * ARWeight.CONTENT + ar.common_c_keys_sim * ARWeight.C_KEY + \
                                 ar.common_e_keys_sim * ARWeight.E_KEY + ar.common_journal_sim * ARWeight.JOURNAL + \
                                 ar.common_org_sim * ARWeight.ORG + ar.common_papers_sim * ARWeight.PAPER + \
                                 ar.common_years_sim * ARWeight.YEAR

                # 剔除一些 得分低的用户关系
                if ar.final_score < 0.1 or (ar.common_c_keys_sim < 0.3 and ar.common_org == 0 and ar.common_papers == 0
                                            and ar.final_score < 0.3):
                    del ar_common

                    del ar

                    continue

                # flag代表了 相似度的一种等级关系

                if ar.final_score >= 0.3 and ar.common_papers >= 1 and ar.common_org >= 1:

                    flag = 1

                elif ar.common_papers >= 1 and ar.common_org >= 1:

                    flag = 2

                elif ar.common_papers >= 1:

                    flag = 3

                elif ar.common_org >= 1:

                    flag = 4

                elif ar.final_score >= 0.3:

                    flag = 5

                elif ar.common_c_keys_sim >= 0.4 and ar.paper_content_sim >= 0.3:

                    flag = 6

                elif ar.common_c_keys_sim >= 0.4:

                    flag = 7

                elif ar.paper_content_sim >= 0.3:

                    flag = 8

                else:

                    flag = 0

                self.author_relations.append(AuthorRelationData(author_1, author_2, ar.final_score, flag, ar_common))

    @staticmethod
    def get_author_relation_common(rl_1, rl_2, r_com):
        """ 计算 作者之间 相似度 """

        if not rl_1 or not rl_2 or not len(rl_1) or not len(rl_2):

            return 0

        common = 0

        for r in rl_1:

            if r in rl_2:

                common += 1

                if r not in r_com:

                    r_com.append(r)

        return common

    @staticmethod
    def calculate_paper_sim(paps_1, paps_2, stop_words):
        """ 计算文章相似性 累加文章简介c_abs 计算内容相似度 """

        if not paps_1 or not paps_2 or not len(paps_1) or not len(paps_2):

            return 0

        pap_1_desc = pap_2_desc = ''

        for i in range(len(paps_1)):

            if not i:  # i == 0 的时候 第一次计算

                pap_1_desc = paps_1[i].c_abs

            else:

                pap_1_desc += ' ' + paps_1[i].c_abs

        for i in range(len(paps_2)):

            if i == 0:

                pap_2_desc = paps_2[i].c_abs

            else:

                pap_2_desc += ' ' + paps_2[i].c_abs

        return AuthorGenerator.calculate_sim(pap_1_desc, pap_2_desc, stop_words)

    @staticmethod
    def calculate_sim(desc_1, desc_2, stop_words):
        """ 计算 内容(字符串) 相似性 """

        if not desc_1 or not desc_2 or not len(desc_1) or not len(desc_2):

            return 0

        desc_l_1 = re.split(' ', Convert.remove_stop_word(desc_1, stop_words))

        desc_l_2 = re.split(' ', Convert.remove_stop_word(desc_2, stop_words))

        com = 0.0

        for d in desc_l_1:  # 剔除空内容

            if not d or not len(d.strip()):

                desc_l_1.remove(d)

        for d in desc_l_2:

            if not d or not len(d.strip()):

                desc_l_2.remove(d)

        for d_1 in desc_l_1:

            for d_2 in desc_l_2:

                if d_1 == d_2:

                    desc_l_2.remove(d_2)

                    com += 1

                    break

        return com / (len(desc_l_1) + len(desc_l_2))


class HotResearchGenerator(object):
    """ 科研热点预测生成 """

    def __init__(self, papers):

        if not papers or not len(papers):

            raise(BaseException, '参数不能为空')

        self.papers = papers

        self.topic_paps = {}

        self.hot_researches = []

    def generate_hot_research(self):

        # 在转化上很费时间
        Convert.paper2topic_paps(self.papers, self.topic_paps)

        print('数据转化完毕 删除papers。。。')

        del self.papers  # 清空占用的内存空间

        self.topic_prediction()

    def topic_prediction(self):
        """ 研究热点预测 """

        for topic in self.topic_paps.keys():

            pap_info = self.topic_paps[topic]

            yrt = {}  # year:paper

            hot_degree = HotDegree()

            hot_degree.pap_num = len(pap_info.c_titles)

            for paper in pap_info.paps:

                Convert.paper2year_paps(paper, yrt)

            temp_hot = Convert.generate_hot_degree(hot_degree, yrt)

            hot_degree.hot = Convert.calculate_hot_degree_by_pap(hot_degree, pap_info, temp_hot)

            self.hot_researches.append(HotResearchData(topic, pap_info, hot_degree))


class TopicOntologyGenerator(object):

    def __init__(self, topics):

        if not topics or not len(topics):

            raise(BaseException, '参数不能为空')

        self.topics = topics

        self.prob_edge = {}

        self.vertex = {}

        self.edge = {}

        self.results = []

    def generate_topic_ontology(self):
        """ 亚本体抽取 """

        Graph.generate_graphic(self.topics, self.vertex, self.edge)

        Graph.generate_direction_graphic(self.vertex, self.edge)

        # TODO 需要优化的地方 假如 进入执行十分耗时。

        # matrix = CommonGraph.get_reachable_matrix(vertex, edge)

        # CommonGraph.cut_simple_path(vertex, edge, matrix)

        # del matrix

        self.assign_edge_prob(self.vertex, self.edge)

    def assign_edge_prob(self, vertex, edge):

        for edge_key in edge:

            keys = re.split(' ', edge_key)

            weight_head = vertex[keys[0]]

            weight_tail = vertex[keys[1]]

            # 两个 topic 之间的概率为 = 边的权 ／（ 顶点的权 + 尾点的权 ）
            prob = 2 * float(edge[edge_key]) / (weight_head + weight_tail)

            self.prob_edge[edge_key] = str(edge[edge_key]) + ' ' + str(prob)

    def generate_full_ontology(self):
        """ 全体关系的亚本体抽取 """

        self.generate_topic_ontology()

        print(len(self.vertex), len(self.prob_edge))

        self.calculate_full_ontology()

    def generate_equal_relation(self):
        """ 等价关系 """

        self.generate_topic_ontology()

        for v_head in self.vertex:

            k = 0

            for v_tail in self.vertex:

                edge_key = v_head + ' ' + v_tail

                if k > self.vertex[v_head]:

                    break

                if v_head == v_tail:

                    continue

                if edge_key in self.prob_edge:

                    words = re.split(' ', self.prob_edge[edge_key])

                    k += float(words[0])

                    for v in self.vertex:

                        if v == v_head or v == v_tail:

                            continue
                        if k > self.vertex[v_head]:

                            break

                        edge_key1 = v_head + ' ' + v

                        if edge_key1 in self.prob_edge:

                            words = re.split(' ', self.prob_edge[edge_key])

                            k += float(words[0])

                            if abs(self.vertex[v_tail] - self.vertex[v]) <= 3:

                                rst = 'E'

                            else:

                                rst = 'NE'

                            print(v_tail, v, rst, v_head)

    def calculate_full_ontology(self):

        stop_words = Convert.get_stop_word()

        for vertex_head in self.vertex:

            for vertex_tail in self.vertex:

                edge_key = vertex_head + ' ' + vertex_tail

                if edge_key in self.prob_edge:

                    words = re.split(' ', self.prob_edge[edge_key])

                    co_occurrence = float(words[0])  # edge 的权值

                    if co_occurrence < ORWeight.OCCURRENCE:

                        continue

                    cf = 2 * co_occurrence / (self.vertex[vertex_head] + self.vertex[vertex_tail])

                    #  大于 3 为 层次关系
                    if self.vertex[vertex_head] - self.vertex[vertex_tail] >= ORWeight.HIERARCHY:

                        rst = 'H '

                    else:

                        rst = 'NH '

                    # 小与 3 为等价关系
                    if self.vertex[vertex_head] - self.vertex[vertex_tail] <= ORWeight.EQUIVALENCE:

                        rst += 'E '

                    else:

                        rst += 'NE '

                    # 子类关系判定
                    if self.vertex[vertex_head] >= ORWeight.SUBCLASS[0] and self.vertex[vertex_tail] >= ORWeight.SUBCLASS[1]:

                        rst += 'S '

                    else:

                        rst += 'NS '

                    # 整体部分关系判定
                    if self.vertex[vertex_head] >= ORWeight.MERONYMY[0] and self.vertex[vertex_tail] >= ORWeight.MERONYMY[1]:

                        rst += 'M '

                    else:

                        rst += 'NM '

                    if ORWeight.INSTANCE[0] <= self.vertex[vertex_head] <= ORWeight.INSTANCE[1] \
                            and ORWeight.INSTANCE[2] <= self.vertex[vertex_tail] <= ORWeight.INSTANCE[3] \
                            and AuthorGenerator.calculate_sim(vertex_head, vertex_tail, stop_words) > ORWeight.INSTANCE[4]:

                        rst += 'I '

                    else:

                        rst += 'NI '

                    self.results.append(FullOntoData(edge_key, co_occurrence, rst, cf, self.prob_edge[edge_key]))


class YearOntologyGenerator(object):
    """ 时间 本体聚类 """

    def __init__(self, papers):

        if not papers or not len(papers):

            raise(BaseException, '参数不能为空')

        self.papers = papers

    def generate_year_ontology(self):

        self.paper_selection()

        time_chain = self.get_time_chain()

        concept_cluster = self.get_concept_cluster(time_chain)

        vertex = self.get_vertex()

        self.get_year_relation_graph(time_chain, concept_cluster, vertex)

    def paper_selection(self):
        """ 论文数据选择 删除 空的数据 和 作者发表论文较少的数据 """

        target_papers = []

        for paper in self.papers:

            if not paper.year or not paper.c_journal or not paper.c_title or not paper.c_org or not paper.c_keys or not paper.c_authors:

                continue

            author_value = 0

            authors = re.split(' |;|；', paper.c_authors)

            if len(authors):

                for p in self.papers:

                    temp_authors = p.c_authors

                    if temp_authors:

                        if not len(temp_authors.strip()):
                            continue

                        for author in authors:

                            if author and temp_authors.find(author) >= 0:

                                author_value += 1

                                break

            if author_value > 2:

                target_papers.append(paper)

        self.papers = target_papers

    def get_time_chain(self):
        """ time_chain 是 key 和 year_info 的字典 其中year_info 又是year 和 ConceptAttribution 的字典 """

        time_chain = {}

        for paper in self.papers:

            topics = re.split(' |;|；', paper.c_keys)

            year = paper.year

            for topic in topics:

                if not topic:

                    continue

                if topic in time_chain:

                    year_info = time_chain[topic]

                else:

                    year_info = {}

                    time_chain[topic] = year_info

                if year in year_info:

                    con_att = year_info[year]

                else:

                    con_att = ConceptAttribution()

                    year_info[year] = con_att

                c_journal = paper.c_journal.replace(' ', '').strip()

                c_title = paper.c_title.replace(' ', '').strip()

                if c_journal not in con_att.journals:

                    con_att.journals.append(c_journal)

                if c_title not in con_att.titles:

                    con_att.titles.append(c_title)

                orgs = re.split(' |;|；', paper.c_org.replace(' ', ''))

                for org in orgs:

                    if org and org not in con_att.org_list:

                        con_att.org_list.append(org)

                researchers = re.split(' |;|；', paper.c_authors.replace(' ', ''))

                for researcher in researchers:

                    if researcher and researcher not in con_att.researchers:

                        con_att.researchers.append(researcher)

                keys = re.split(' |;|；', paper.c_keys.replace(' ', ''))

                for key in keys:

                    if key and key not in con_att.relate_topic:

                        con_att.relate_topic.append(key)

        return time_chain

    @staticmethod
    def get_concept_cluster(time_chain):
        """ 为每一个概念进行聚类 """

        rst = {}

        for topic in time_chain:

            year_info = time_chain[topic]

            years = year_info.keys()

            years.sort()

            k = len(year_info)

            clusters = []

            if k <= 3:

                year = years[k - 1]

                clusters.append(year)

                rst[topic] = clusters

                continue

            for index in range(k - 1):

                year1 = years[index - 1]

                con_att1 = year_info[year1]

                year2 = years[index]

                con_att2 = year_info[year2]

                year3 = years[index + 1]

                con_att3 = year_info[year3]

                d1 = YearOntologyGenerator.is_split(con_att1, con_att2)

                d2 = YearOntologyGenerator.is_split(con_att2, con_att3)

                d3 = YearOntologyGenerator.is_split(con_att1, con_att3)

                if abs(d1) >= 0.3 and abs(d2) >= 0.3 and abs(d3) >= 0.3 and d1 * d2 < 0 and d2 * d3 > 0:
                    # 这里 key2 是拐点 一个可以将topic分类的点

                    year = years[index]

                    if topic in rst:

                        clusters = rst[topic]

                        if len(clusters) > 1:

                            dist = int(year) - int(clusters[len(clusters) - 1])

                            if dist > 2:

                                clusters.append(year)

                                rst[topic] = clusters

                            if len(clusters) > 4:  # 需要合并聚类点

                                y_min = 11111111

                                index_min = -1

                                for m, year in enumerate(clusters):

                                    year0 = int(clusters[m - 1])

                                    if abs(year - year0) < y_min:

                                        y_min = abs(year - year0)

                                        index_min = m

                                del clusters[index_min]

                            rst[topic] = clusters

                        else:

                            clusters.append(year)

                            rst[topic] = clusters
                    else:

                        clusters.append(year)

                        rst[topic] = clusters

            if topic not in rst:

                year = years[k - 1]

                clusters = list()

                clusters.append(year)

                rst[topic] = clusters

                continue

        return rst

    @staticmethod
    def is_split(con_att1, con_att2):
        ''' 利用变换率计算是否要分隔聚类点 也就是说当两者内容相似的时候，其实所得结果很小 '''

        if not con_att1 or not con_att2:
            return 0.0

        f1 = f2 = f3 = f4 = f5 = 0.0

        if len(con_att1.titles):
            f1 = float(len(con_att2.titles) - len(con_att1.titles)) / len(con_att1.titles)

        if len(con_att1.researchers):
            f2 = float(len(con_att2.researchers) - len(con_att1.researchers)) / len(con_att1.researchers)

        if len(con_att1.relate_topic):
            f3 = float(len(con_att2.relate_topic) - len(con_att1.relate_topic)) / len(con_att1.relate_topic)

        if len(con_att1.journals):
            f4 = float(len(con_att2.journals) - len(con_att1.journals)) / len(con_att1.journals)

        if len(con_att1.org_list):
            f5 = float(len(con_att2.org_list) - len(con_att1.org_list)) / len(con_att1.org_list)

        return f1 * 0.25 + f2 * 0.25 + f3 * 0.2 + f4 * 0.1 + f5 * 0.2

    def get_vertex(self):
        """ 得到 topic 的无向图 """

        vertex = {}

        for i, s in enumerate(self.papers):

            topics = re.split(' |;|；', s.c_keys)

            if len(topics) <= 1:

                continue

            for j, topic in enumerate(topics):

                if not topic:

                    continue

                if topic in vertex:

                    vertex[topic] += len(topics) - j

                else:

                    vertex[topic] = len(topics) - j

            authors = re.split(' |;|；', s.c_authors)

            if len(authors) > 0:

                b = i + 1

                while b < len(self.papers):

                    s2 = self.papers[b]

                    if s == s2:
                        continue

                    temp = s2.c_authors

                    if not len(temp.strip()):
                        continue

                    for author in authors:

                        if author:

                            if author in temp:

                                words = re.split(' |;|；', s2.c_keys)

                                if len(words) <= 1:
                                    continue

                                for j, word in enumerate(words):

                                    if not word:
                                        continue

                                    if word in vertex:

                                        vertex[word] += (len(words) - j) * 0.85

                                    else:

                                        vertex[word] = (len(words) - j) * 0.85

                            break

                    b += 1

        return vertex

    @staticmethod
    def get_year_relation_graph(time_chain, concept_cluster, vertex):
        """ 进行关系分配得到本体图 """

        for v1 in vertex:

            if vertex[v1] <= 0:
                continue

            for v2 in vertex:

                if vertex[v2] <= 0:
                    continue

                if v1.strip() == v2.strip():
                    continue

                if vertex[v1] < vertex[v2]:
                    continue

                clu1 = concept_cluster[v1]

                clu2 = concept_cluster[v2]

                pd1 = YearOntologyGenerator.get_concept_cluster_value(clu1)

                pd2 = YearOntologyGenerator.get_concept_cluster_value(clu2)

                pdict = 1 / (1 + abs(pd1 - pd2))  # 两个概念间的 距离

                con_atts = YearOntologyGenerator.get_attr_sim(v1, v2, time_chain, concept_cluster)  # 属性相似度

                deg_sim = pdict * vertex[v1] / vertex[v2]

                attr_sim = pdict * (con_atts[0] + con_atts[1] + (CASWeight.f3 * abs(vertex[v1] - vertex[v2]) / vertex[v1]))

                rell = ''

                if deg_sim > RRWeight.s1 and con_atts[3] >= 1:

                    rell += 'H_'

                    if RRWeight.s3 <= con_atts[2] < 1:

                        rell += 'I_'

                elif attr_sim > RRWeight.s2:

                    rell += 'E_'

                elif attr_sim < RRWeight.s4 and pdict > RRWeight.s5:

                    continue

                elif (deg_sim == 1 and con_atts[3] <= 1) or con_atts[2] == 1:

                    rell += 'HE_'

                else:

                    rell += 'HI_'

                print(v1, v2, rell)

    @staticmethod
    def get_concept_cluster_value(source):

        return {1: 0.0, 2: 0.2, 3: 0.5, 4: 0.5}.get(len(source), 0.0)

    @staticmethod
    def get_attr_sim(topic, topic1, time_chain, concept_cluster):

        rst = []

        att = time_chain[topic]

        att1 = time_chain[topic1]

        cluster = concept_cluster[topic]

        cluster1 = concept_cluster[topic1]

        all_att = ConceptAttribution()

        all_att1 = ConceptAttribution()

        concept_min_year = concept_min_year1 = 2029

        index = 1979

        while index < 2011:

            year = str(index)

            if year in att:

                year_info = att[year]

                Convert.append2list(all_att.journals, year_info.journals)
                Convert.append2list(all_att.org_list, year_info.org_list)
                Convert.append2list(all_att.relate_topic, year_info.relate_topic)
                Convert.append2list(all_att.researchers, year_info.researchers)
                Convert.append2list(all_att.titles, year_info.titles)

                if index < concept_min_year:
                    concept_min_year = index

            if year in att1:

                year_info1 = att1[year]

                Convert.append2list(all_att1.journals, year_info1.journals)
                Convert.append2list(all_att1.org_list, year_info1.org_list)
                Convert.append2list(all_att1.relate_topic, year_info1.relate_topic)
                Convert.append2list(all_att1.researchers, year_info1.researchers)
                Convert.append2list(all_att1.titles, year_info1.titles)

                if index < concept_min_year1:
                    concept_min_year1 = index

            index += 1

        gen_sim = ConceptAttributionSim()

        gen_sim.journals_sim = 2.0 * YearOntologyGenerator.get_common_attr(all_att.journals, all_att1.journals) if len(all_att.journals) + len(
            all_att1.journals) else 0

        gen_sim.org_list_sim = 2.0 * YearOntologyGenerator.get_common_attr(all_att.org_list, all_att1.org_list) if len(
            all_att.org_list) + len(all_att1.org_list) else 0

        gen_sim.relate_topic_sim = 2.0 * YearOntologyGenerator.get_common_attr(all_att.relate_topic, all_att1.relate_topic) if len(
            all_att.relate_topic) + len(all_att1.relate_topic) else 0

        gen_sim.researchers_sim = 2.0 * YearOntologyGenerator.get_common_attr(all_att.researchers, all_att1.researchers) if len(
            all_att.researchers) + len(all_att1.researchers) else 0

        gen_sim.titles_sim = 2.0 * YearOntologyGenerator.get_common_attr(all_att.titles, all_att1.titles) if len(all_att.titles) + len(
            all_att1.titles) else 0

        gen_deg_sim = ConceptAttributionSim()

        if not len(all_att.journals) or not len(all_att1.journals):

            gen_deg_sim.journals_sim = 0

        else:

            gen_deg_sim.journals_sim = len(all_att1.journals) / len(all_att.journals) if len(all_att.journals) > len(
                all_att1.journals) else len(all_att.journals) / len(all_att1.journals)

        if not len(all_att.org_list) or not len(all_att1.org_list):

            gen_deg_sim.org_list_sim = 0

        else:

            gen_deg_sim.org_list_sim = len(all_att1.org_list) / len(all_att.org_list) if len(all_att.org_list) > len(
                all_att1.org_list) else len(all_att.org_list) / len(all_att1.org_list)

        if not len(all_att.relate_topic) or not len(all_att1.relate_topic):

            gen_deg_sim.relate_topic_sim = 0

        else:

            gen_deg_sim.relate_topic_sim = len(all_att1.relate_topic) / len(all_att.relate_topic) if len(
                all_att.relate_topic) > len(all_att1.relate_topic) else len(all_att.relate_topic) / len(
                all_att1.relate_topic)

        if not len(all_att.researchers) or not len(all_att1.researchers):

            gen_deg_sim.researchers_sim = 0

        else:

            gen_deg_sim.researchers_sim = len(all_att1.researchers) / len(all_att.researchers) if len(
                all_att.researchers) > len(all_att1.researchers) else len(all_att.researchers) / len(
                all_att1.researchers)

        if not len(all_att.titles) or not len(all_att1.titles):

            gen_deg_sim.titles_sim = 0

        else:

            gen_deg_sim.titles_sim = len(all_att1.titles) / len(all_att.titles) if len(all_att.titles) > len(
                all_att1.titles) else len(all_att.titles) / len(all_att1.titles)

        sim1 = CASWeight.a1 * (CASWeight.tup1 * gen_sim.titles_sim +
                               CASWeight.tup2 * gen_sim.researchers_sim +
                               CASWeight.tup3 * gen_sim.journals_sim +
                               CASWeight.tup4 * gen_sim.org_list_sim +
                               CASWeight.tup5 * gen_sim.relate_topic_sim)

        sim1 += CASWeight.a2 * (CASWeight.tup1 * gen_deg_sim.titles_sim +
                                CASWeight.tup2 * gen_deg_sim.researchers_sim +
                                CASWeight.tup3 * gen_deg_sim.journals_sim +
                                CASWeight.tup4 * gen_deg_sim.org_list_sim +
                                CASWeight.tup5 * gen_deg_sim.relate_topic_sim)

        sim1 = sim1 * CASWeight.f1

        beg = end = 1970

        period_sim = ConceptAttributionSim()

        deg_att = ConceptAttributionSim()

        deg_att1 = ConceptAttributionSim()

        deg_sim = ConceptAttributionSim()

        cluster_min = int(len(cluster1)) if int(len(cluster)) > int(len(cluster1)) else int(len(cluster))

        for i in range(cluster_min):

            year1 = int(cluster[i])

            year2 = int(cluster1[i])

            end = year2 if year1 > year2 else year1

            while beg <= end:

                beg += 1

                year_key = str(beg)

                if year_key in att and year_key in att1:

                    year_info1 = att[year_key]

                    year_info2 = att1[year_key]

                    period_sim.journals_sim = 2.0 * YearOntologyGenerator.get_common_attr(year_info1.journals, year_info2.journals) / (
                    len(year_info1.journals) + len(year_info2.journals)) if len(year_info1.journals) + len(
                        year_info2.journals) else 0

                    period_sim.org_list_sim = 2.0 * YearOntologyGenerator.get_common_attr(year_info1.org_list, year_info2.org_list) / (
                    len(year_info1.org_list) + len(year_info2.org_list)) if len(year_info1.org_list) + len(
                        year_info2.org_list) else 0

                    period_sim.relate_topic_sim = 2.0 * YearOntologyGenerator.get_common_attr(year_info1.relate_topic,
                                                                                              year_info2.relate_topic) / (
                                                  len(year_info1.relate_topic) + len(year_info2.relate_topic)) if len(
                        year_info1.relate_topic) + len(year_info2.relate_topic) else 0

                    period_sim.researchers_sim = 2.0 * YearOntologyGenerator.get_common_attr(year_info1.researchers,
                                                                                             year_info2.researchers) / (
                                                 len(year_info1.researchers) + len(year_info2.researchers)) if len(
                        year_info1.researchers) + len(year_info2.researchers) else 0

                    period_sim.titles_sim = 2.0 * YearOntologyGenerator.get_common_attr(year_info1.titles, year_info2.titles) / (
                    len(year_info1.titles) + len(year_info2.titles)) if len(year_info1.titles) + len(
                        year_info2.titles) else 0

                    deg_att.journals_sim += len(year_info1.journals)

                    deg_att.org_list_sim += len(year_info1.org_list)

                    deg_att.relate_topic_sim += len(year_info1.relate_topic)

                    deg_att.researchers_sim += len(year_info1.researchers)

                    deg_att.titles_sim += len(year_info1.titles)

                    deg_att1.journals_sim += len(year_info2.journals)

                    deg_att1.org_list_sim += len(year_info2.org_list)

                    deg_att1.relate_topic_sim += len(year_info2.relate_topic)

                    deg_att1.researchers_sim += len(year_info2.researchers)

                    deg_att1.titles_sim += len(year_info2.titles)

            beg = year1 if year1 > year2 else year2

        if not deg_att.journals_sim or not deg_att1.journals_sim:

            deg_sim.journals_sim = 0

        else:

            deg_sim.journals_sim = deg_att1.journals_sim / deg_att.journals_sim if deg_att.journals_sim > deg_att1.journals_sim else deg_att.journals_sim / deg_att1.journals_sim

        if not deg_att.org_list_sim or not deg_att1.org_list_sim:

            deg_sim.org_list_sim = 0

        else:

            deg_sim.org_list_sim = deg_att1.org_list_sim / deg_att.org_list_sim if deg_att.org_list_sim > deg_att1.org_list_sim else deg_att.org_list_sim / deg_att1.org_list_sim

        if not deg_att.relate_topic_sim or not deg_att1.relate_topic_sim:

            deg_sim.relate_topic_sim = 0

        else:

            deg_sim.relate_topic_sim = deg_att1.relate_topic_sim / deg_att.relate_topic_sim if deg_att.relate_topic_sim > deg_att1.relate_topic_sim else deg_att.relate_topic_sim / deg_att1.relate_topic_sim

        if not deg_att.researchers_sim or not deg_att1.researchers_sim:

            deg_sim.researchers_sim = 0

        else:

            deg_sim.researchers_sim = deg_att1.researchers_sim / deg_att.researchers_sim if deg_att.researchers_sim > deg_att1.researchers_sim else deg_att.researchers_sim / deg_att1.researchers_sim

        if not deg_att.titles_sim or not deg_att1.titles_sim:

            deg_sim.titles_sim = 0

        else:

            deg_sim.titles_sim = deg_att1.titles_sim / deg_att.titles_sim if deg_att.titles_sim > deg_att1.titles_sim else deg_att.titles_sim / deg_att1.titles_sim

        sim2 = CASWeight.a1 * (CASWeight.tup1 * period_sim.titles_sim +
                               CASWeight.tup2 * period_sim.researchers_sim +
                               CASWeight.tup3 * period_sim.journals_sim +
                               CASWeight.tup4 * period_sim.org_list_sim +
                               CASWeight.tup5 * period_sim.relate_topic_sim)

        sim2 += CASWeight.a2 * (CASWeight.tup1 * deg_sim.titles_sim +
                                CASWeight.tup2 * deg_sim.researchers_sim +
                                CASWeight.tup3 * deg_sim.journals_sim +
                                CASWeight.tup4 * deg_sim.org_list_sim +
                                CASWeight.tup5 * deg_sim.relate_topic_sim)

        sim2 = sim2 * CASWeight.f2

        rst.append(sim1)

        rst.append(sim2)

        rst.append(YearOntologyGenerator.get_str_sim(topic, topic1))

        if concept_min_year != 2029 and concept_min_year1 != 2029:

            rst.append(concept_min_year1 - concept_min_year)

        return rst

    @staticmethod
    def get_common_attr(l_str1, l_str2):

        rst = 0

        for str1 in l_str1:

            for str2 in l_str2:

                if str1.strip() == str2.strip():
                    rst += 1

        return rst

    @staticmethod
    def get_str_sim(str1, str2):

        com = 0.0

        for i in range(len(str1)):

            if str1[i] in str2:
                com += 1

        return com * 2 / len(str1) + len(str2)
