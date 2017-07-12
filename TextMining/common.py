# coding=utf-8
import os
import re
from data import OrgResearchTopic, YearResearchTopic, JournalResearchTopic, PaperInfo


class Convert(object):
    """ 把 paper 信息 转化为 其他类信息"""

    @staticmethod
    def paper2other(paper_item, other_item):
        """ 把 paper 的信息注入到 其他数据 中"""

        if not paper_item:

            return

        keys = re.split(';|；', paper_item)

        for key in keys:

            if len(key.strip()) and key not in other_item:

                other_item.append(key)

    @staticmethod
    def paper2journal_paps(paper, journal_paps_info):
        """ 把 paper 的信息注入到 JournalResearchTopic 中"""

        if paper.c_journal:

            journals = re.split(';；', paper.c_journal)

            for journal in journals:

                if journal not in journal_paps_info:

                    jrt = JournalResearchTopic()

                    journal_paps_info[journal] = jrt

                else:

                    jrt = journal_paps_info[journal]

                Convert.paper2other(paper.c_org, jrt.org_list)
                Convert.paper2other(paper.c_keys, jrt.relate_topic)
                Convert.paper2other(paper.c_authors, jrt.researchers)
                Convert.paper2other(paper.c_title, jrt.titles)

                if paper not in jrt.paps:

                    jrt.paps.append(paper)

    @staticmethod
    def paper2org_paps(paper, org_paps_info):
        """ 把 paper 的信息注入到 OrgResearchTopic 中"""

        if paper.c_org:

            orgs = re.split(';；', paper.c_org)

            for org in orgs:

                if org not in org_paps_info:

                    ort = OrgResearchTopic()

                    org_paps_info[org] = ort

                else:

                    ort = org_paps_info[org]

                Convert.paper2other(paper.c_journal, ort.journal_list)
                Convert.paper2other(paper.c_keys, ort.relate_topic)
                Convert.paper2other(paper.c_authors, ort.researchers)
                Convert.paper2other(paper.c_title, ort.titles)

                if paper not in ort.paps:

                    ort.paps.append(paper)

    @staticmethod
    def paper2year_paps(paper, year_paps_info):
        """ 把 paper 的信息注入到 YearResearchTopic 中 """

        if paper.year not in year_paps_info:

            yrt = YearResearchTopic()

            year_paps_info[paper.year] = yrt

        else:

            yrt = year_paps_info[paper.year]

        Convert.paper2other(paper.c_journal, yrt.journal_list)
        Convert.paper2other(paper.c_keys, yrt.relate_topic)
        Convert.paper2other(paper.c_authors, yrt.researchers)
        Convert.paper2other(paper.c_title, yrt.titles)
        Convert.paper2other(paper.c_org, yrt.org_list)

        if paper not in yrt.paps:

            yrt.paps.append(paper)

    @staticmethod
    def paper2author_paps(papers, author_paps):
        """ 填充 单个 data 基本数据得到 作者-论文 ：author_paps """

        for paper in papers:

            if not paper.c_authors:

                continue

            authors = re.split(';|；| ', paper.c_authors)

            for author in authors:

                if author in author_paps:

                    pi = author_paps[author]

                else:

                    pi = PaperInfo()

                    author_paps[author] = pi

                Convert.paper2other(paper.c_keys, pi.c_keys)
                Convert.paper2other(paper.e_keys, pi.e_keys)
                Convert.paper2other(paper.c_journal, pi.c_journals)
                Convert.paper2other(paper.c_org, pi.org)
                Convert.paper2other(paper.year, pi.years)
                Convert.paper2other(paper.c_title, pi.c_titles)

                if paper not in pi.paps:

                    pi.paps.append(paper)

    @staticmethod
    def paper2topic_paps(papers, topic_paps):
        """ 填充 单个 data 基本数据得到 研究点-论文 topic_paps """

        for paper in papers:

            if not paper.c_authors or not len(paper.c_authors):

                continue

            # TODO 不明白为什么判断 org
            if paper.c_org is None or len(paper.c_org) == 0:

                continue

            if not paper.c_keys:

                continue

            keys = re.split(';|；', paper.c_keys)

            for key in keys:

                if not key or not len(key.strip()):

                    continue

                if key in topic_paps:

                    pi = topic_paps[key]

                else:

                    pi = PaperInfo()

                    topic_paps[key] = pi

                Convert.paper2other(paper.c_keys, pi.c_keys)
                Convert.paper2other(paper.e_keys, pi.e_keys)
                Convert.paper2other(paper.c_journal, pi.c_journals)
                Convert.paper2other(paper.c_org, pi.org)
                Convert.paper2other(paper.year, pi.years)
                Convert.paper2other(paper.c_title, pi.c_titles)

                if paper not in pi.paps:

                    pi.paps.append(paper)

    @staticmethod
    def get_stop_word():
        """停词表 """

        stop_words = []

        f = open(os.getcwd() + '/TextMining/file/StopWords.txt', 'r')

        lines = f.readlines()

        for line in lines:

            if line and len(line):

                stop_words.append(line.strip())

        f.close()

        return stop_words

    @staticmethod
    def remove_stop_word(desc, stop_words):
        """ 去掉内容中的停词 """
        if desc:

            for stop in stop_words:

                desc = desc.replace(stop, '')

        return desc

    @staticmethod
    def generate_hot_degree(hot_degree, year_paps_info):
        """ 计算研究热度 """

        if len(year_paps_info) > 0:  # 计算平均每年的论文数目

            hot_degree.avg_pap_year = float(hot_degree.pap_num) / len(year_paps_info)

        years = year_paps_info.keys()

        years.sort()  # 年信息 为正序

        year_threshold = 0  # 仅仅统计的信息为近三年

        pap_num = 0

        hot = 0

        for i in range(len(years)):

            i_reverse = len(years) - i - 1

            year_recent = years[i_reverse]

            hot_degree.recent_3year += ' ' + year_recent

            yrt = year_paps_info[year_recent]  # 获取最近几年的 paper 信息

            pap_num += len(yrt.paps)  # 累加论文数目

            if i_reverse:

                pre_year_recent = year_paps_info[years[i_reverse - 1]]

                if len(pre_year_recent.paps):  # 论文增加率 =（当年的论文数 - 前一年的论文数）／ 前一年的论文数

                    hot_degree.pap_increment_3year.append(float(len(yrt.paps) - len(pre_year_recent.paps))
                                                                      / len(pre_year_recent.paps))
                    hot += 1  # 当有近年的信息时 热度++

                if len(pre_year_recent.relate_topic):

                    hot_degree.key_increment_3year.append(float(len(yrt.relate_topic) - len(pre_year_recent.relate_topic))
                                                                       / len(pre_year_recent.relate_topic))
                    hot += 1

                if len(pre_year_recent.researchers):

                    hot_degree.person_increment_3year.append(float(len(yrt.researchers) - len(pre_year_recent.researchers))
                                                                         / len(pre_year_recent.researchers))
                    hot += 1

                if len(pre_year_recent.org_list):

                    hot_degree.org_increment_3year.append(float(len(yrt.org_list) - len(pre_year_recent.org_list))
                                                                      / len(pre_year_recent.org_list))
                    hot += 1

                if len(pre_year_recent.journal_list):

                    hot_degree.journal_increment_3year.append(float(len(yrt.journal_list) - len(pre_year_recent.journal_list))
                                                                       / len(pre_year_recent.journal_list))
                    hot += 1
            else:

                break

            year_threshold += 1

            if year_threshold == 3:

                break

        hot_degree.avg_pap_3year = float(pap_num) / 3

        hot += int(hot_degree.avg_pap_3year) / hot_degree.avg_pap_year

        return hot

    @staticmethod
    def calculate_hot_degree_by_survey(survey, hot):

        if survey.hot_degree.avg_pap_year > 10:
            hot += 1

        if survey.hot_degree.avg_pap_3year > 10:
            hot += 1

        if len(survey.journal_list) > 5:
            hot += 1

        if len(survey.org_list) > 10:
            hot += 1

        if len(survey.researcher_list) > 100:
            hot += 1

        if len(survey.year_list) > 10:
            hot += 1

        if len(survey.title_list) > 150:
            hot += 1

        return float(hot) / 23

    @staticmethod
    def calculate_hot_degree_by_pap(hot_degree, pap_info, hot):

        if hot_degree.avg_pap_year > 10:
            hot += 1

        if hot_degree.avg_pap_3year > 10:
            hot += 1

        if len(pap_info.c_journals) > 5:
            hot += 1

        if len(pap_info.org) > 10:
            hot += 1

        if len(pap_info.c_titles) > 150:
            hot += 1

        if len(pap_info.years) > 10:
            hot += 1

        return float(hot) / 22

    @staticmethod
    def append2list(source, target):

        for t in enumerate(target):

            if t in source:

                source.append(t)


class Graph(object):

    @staticmethod
    def generate_graphic(topics, vertex, edge):
        """ 生成无向图 vertex 记录 topic: 点的权 . edge 记录 topic-topic: 边的权 """

        for topic in topics:

            key_words = re.split(' |;|；', topic)

            if len(key_words) <= 1:

                continue

            for vertex_key1 in key_words:

                if not vertex_key1.strip():

                    continue

                if vertex_key1 in vertex:

                    vertex[vertex_key1] += len(key_words) - 1

                else:

                    vertex[vertex_key1] = len(key_words) - 1

                for vertex_key2 in key_words:

                    if not vertex_key2.strip() or vertex_key2 == vertex_key1:

                        continue

                    edge_key = vertex_key1 + ' ' + vertex_key2

                    if edge_key in edge:

                        edge[edge_key] += 1

                    else:

                        edge[edge_key] = 1

    @staticmethod
    def generate_direction_graphic(vertex, edge):
        """ 得到有向图： 去掉重复的边 形成单向边 """

        for v_head in vertex:

            if not vertex[v_head]:

                continue

            for v_tail in vertex:

                if not vertex[v_tail]:

                    continue

                edge_key = v_head + ' ' + v_tail

                edge_key_reverse = v_tail + ' ' + v_head

                if vertex[v_head] > vertex[v_tail] and edge_key_reverse in edge:

                    del edge[edge_key_reverse]

                elif vertex[v_head] < vertex[v_tail] and edge_key in edge:

                    del edge[edge_key]

    @staticmethod
    def get_reachable_matrix(vertex, edge):
        """ 可达矩阵 """

        matrix = {}

        for e_key in edge:

            matrix[e_key] = edge[e_key]

        for v_before in vertex:

            for v_end in vertex:

                if v_before == v_end:

                    continue

                edge_key = v_before + ' ' + v_end

                for v_mid in vertex:

                    before_mid = v_before + ' ' + v_mid

                    mid_end = v_mid + ' ' + v_end

                    if before_mid in matrix and mid_end in matrix and edge_key in matrix:

                            matrix[edge_key] = int(matrix[before_mid]) + int(matrix[mid_end])

        return matrix

    @staticmethod
    def cut_simple_path(vertex, edge, matrix):
        """ 去除简单路径 """

        for v_before in vertex:

            for v_end in vertex:

                edge_key = v_before + ' ' + v_end

                if edge_key in edge and edge_key in matrix:

                    e_value = edge[edge_key]

                    m_value = edge[edge_key]

                    if e_value and m_value and e_value != m_value:

                        del edge[edge_key]

                        break
