# coding=utf-8
import re
import random
import math
from data import PaperEvaluation, ThemeData
from database import DBHandler, SQL
from common import Convert
# --------------------------------------------------------------------
#  k means 聚类算法


class KMeans(object):

    MAX_FEATURE = 500

    MAX_PAPERS = 200

    MAX_LOOP = 100

    def __init__(self, papers):

        if not papers or not len(papers):

            raise(BaseException, '参数不能为空')

        self.K = 10

        self.papers = papers

        self.method_sentences = []

        self.abstracts = []  # paper 的关键信息简介

        self.features = {}  # paper 提取出来的特征

        self.vectors = []  # 文章 vsm 向量

        self.clusters = []  # 文章 聚类类别

        self.themes = []

    def generate_themes(self):
        """
        流程：1 进行文章筛选：对文章进行评价，然后抽取评价高的文章。 paper_selection
             2 聚类：对文章聚类，从而生成分类的主题信息。 抽取特征->svm->聚类->分类结果
        """
        if len(self.papers) < self.K:  # 论文数目太少

            self.K = len(self.papers)

        self.paper_selection()

        self.generate_feature()

        self.generate_vsm()

        self.clustering()

        self.generate_theme()

    def paper_selection(self):
        """
        筛选论文
        指标：1 作者信息评价指标 作者不仅发表该论文，还发表了其他论文，则评价高
                计算：author_value = 作者论文数目／MAX(作者论文数目)     MAX： 指的是所有文章中MAX
             2 年代信息评价指标 最近几年的文章，评价高
                计算：year_value = 1 / (1 + 当前年 - 发表年)
        评价：最终打分为各评价指标加权和，最难的是如何确定权重，但为了方便，我们自己设置了权重
                计算：final_value = author_weight * author_value + year_weight * year_value
        """
        target_papers = []

        scores = []

        author_weight = 0.7

        year_weight = 0.3

        max_author = 0

        for paper in self.papers:

            if not paper.c_authors:

                self.papers.remove(paper)

                continue

            year = int(paper.year)

            author_value = 0  # 论文的作者 的论文数目， 这里单纯计算数量，并是评价指标！！！

            year_value = 1 / (2011 - year)  # 1 ／ ( 1 + 当前年 - 发表年)

            authors = re.split(' |;|；', paper.c_authors)

            if len(authors):

                for temp_paper in self.papers:

                    temp_authors = temp_paper.c_authors

                    if not temp_authors or not len(temp_authors):

                        continue

                    for temp_author in authors:

                        if temp_author in temp_authors:

                            author_value += 1

                if author_value > max_author:

                    max_author = author_value

            pe = PaperEvaluation()

            pe.author_value = author_value

            pe.year_value = year_value

            scores.append(pe)

        for pe in scores:  # 计算 final value 为什么不在上面计算呢？由于我们需要 MAX(作者论文数目) max_author

            if not pe.author_value:

                pe.final_value = -1

            else:

                pe.final_value = pe.year_value * year_weight + author_weight * pe.author_value / max_author

        if len(self.papers) < KMeans.MAX_PAPERS:

            return

        for index in range(KMeans.MAX_PAPERS):  # 选取 final_value 最大的 paper

            max_score = -1

            max_index = -1

            for i, pe in enumerate(scores):

                if pe.final_value > max_score:

                    max_score = pe.final_value

                    max_index = i

            if max_index >= 0 and self.papers[max_index] not in target_papers:

                target_papers.append(self.papers[max_index])

                scores[max_index].final_value = -1

        self.papers = target_papers

    def generate_feature(self):
        """
        特征提取 文档频数 DF 论文中包涵单词的数量 高频词往往可以代表文章主题
        """

        words_df = {}

        topic_feature = {}

        for paper in self.papers:

            # 从 title abs 中抽取 df feature
            ms = self.method_sentence_extract(paper.c_abs)

            self.method_sentences.append(ms)

            content = paper.c_title + ' ' + ms

            words = re.split(';|；| ', content)

            for word in words:

                if word and len(word) > 1:

                    if word not in words_df:

                        words_df[word] = 1
                    else:

                        words_df[word] += 1

            # 从 keys 中抽取 topic feature 进行本体扩展
            topics_concept = paper.c_keys + ' ' + Convert.remove_stop_word(self.get_key_feature(paper.c_keys), Convert.get_stop_word())

            self.abstracts.append(content + topics_concept)

            topics = re.split(';|；| ', topics_concept)

            for topic in topics:

                if topic and len(topic) > 1:

                    if topic in topic_feature:

                        topic_feature[topic] += 1
                    else:

                        topic_feature[topic] = 1

        # 抽取特征值
        max_num = 0

        # 要选取DF 从小到大依次选择

        word_df_sorted = sorted(words_df.items(), lambda x, y: cmp(y[1], x[1]))

        for df in word_df_sorted:

            if df[0] not in self.features:

                self.features[df[0]] = df[1]

                max_num += 1

                if max_num >= KMeans.MAX_FEATURE:

                    break
            if max_num >= KMeans.MAX_FEATURE:

                break

        max_num = 0

        topic_feature_sorted = sorted(topic_feature.items(), lambda x, y: cmp(x[1], y[1]))

        for topic in topic_feature_sorted:

            if topic[0] not in self.features:

                self.features[topic[0]] = topic[1]

                max_num += 1

                if max_num >= KMeans.MAX_FEATURE:

                    break
            if max_num >= KMeans.MAX_FEATURE:

                break

    def generate_vsm(self):
        """
        向量空间模型（VSM：Vector space model）是最常用的相似度计算模型
        向量为 vectors
        """

        onto_weight = 0.85  # 本体权重调节因子

        method_weight = 0.05  # 方法词权重调节因子

        # 为每一个 paper 形成 vsm 模型
        for doc_num, abstract in enumerate(self.abstracts):

            word_tf = self.get_tf(abstract)  # 获取每个文章的 词频 TF

            doc = []  # paper 的向量

            for feature in self.features:

                feature_sharp = feature + '#'

                if feature in word_tf:

                    if feature in self.method_sentences[doc_num]:

                        weight = 1.0 / self.features[feature] * word_tf[feature] * (1 + method_weight)

                    elif '#' in feature:

                        weight = 1.0 / self.features[feature] * word_tf[feature] * onto_weight

                    else:

                        weight = 1.0 / self.features[feature] * word_tf[feature]

                elif feature_sharp in word_tf:  # 本体扩展词

                    weight = 1.0 / self.features[feature] * word_tf[feature_sharp]

                else:

                    weight = 0.0

                doc.append(weight)

            self.vectors.append(doc)

    def clustering(self):
        """
        算法：
        1 选取k个参照点 doc1 -> dock
        2 对于样本选取对应最近的聚类中心 并分配到类doc中
        3 重新计算聚类中心 在其中选取聚类中心点
        4 形成聚类簇，否则到2循环
        """

        current_center = []  # 聚类中心

        last_center = []

        loop = 0

        # 初始化聚类点
        for i in range(self.K):

            last_center.append(random.randint(0, len(self.vectors)-1))

        while True:

            for doc in self.vectors:

                max_num = -1

                index = -1

                for i in range(self.K):

                    center = last_center[i]

                    distance = self.calculate_cos(doc, self.vectors[center])  # 计算 聚类中心点 和 文章 距离

                    if distance > max_num:

                        max_num = distance

                        index = i

                self.clusters.append(index)

            current_center[:] = []

            for i in range(self.K):  # 重新计算聚类中心点

                current_center.append(self.re_compute_center(i))

            loop += 1
            # 当聚类中心不变 或 循环达到最大次数
            if self.is_terminate(last_center, current_center) or loop > self.MAX_LOOP:

                break

            else:

                self.assign_center(last_center, current_center)  # 更新上一次的聚类中心

                self.clusters[:] = []

    def generate_theme(self):

        for i in range(self.K):

            temp = ''

            papers = []

            for j, paper in enumerate(self.papers):

                if self.clusters[j] == i:

                    temp += paper.c_keys + ' '

                    papers.append(paper)

            if len(temp.strip()):

                words = re.split(';|；| ', temp)

                theme_key = []

                for word in words:

                    word_sharp = word + '#'

                    if (word in self.features or word_sharp in self.features) and word not in theme_key:

                        theme_key.append(word)

                self.themes.append(ThemeData(theme_key, papers))

            else:

                self.themes.append(ThemeData(['空内容聚类', ], papers))

    def re_compute_center(self, index):

        rst = -1

        temp = []

        for i, cluster in enumerate(self.clusters):

            if cluster == index:  # 该文章为 index 类中

                if not len(temp):

                    self.copy_doc(self.vectors[i], temp)

                elif not self.calculate_centroid(temp, self.vectors[i]):

                    return -1

        min_num = 100000

        for j, cluster in enumerate(self.clusters):

            if cluster == index:

                temp1 = self.calculate_cos(self.vectors[j], temp)

                if temp1 < min_num:

                    min_num = temp1

                    rst = j

        return rst

    @staticmethod
    def assign_center(last, current):

        if len(current) != len(last):

            return

        for index, cur in enumerate(current):

            last[index] = cur

    @staticmethod
    def is_terminate(last, current):
        """ 判断结束标志：聚类中心不变 """

        for index, l in enumerate(last):

            if l != current[index]:

                return False

        return True

    @staticmethod
    def calculate_centroid(source, target):
        """ 计算聚类中心 """

        if len(source) != len(target):

            return False

        for index, doc in enumerate(source):

            doc = (doc + target[index]) / 2

        return True

    @staticmethod
    def copy_doc(source, target):

        for doc in source:

            target.append(doc)

    @staticmethod
    def calculate_cos(doc1, doc2):
        """ 计算 cos 也就是两者之间的距离 """

        numerator = KMeans.calculate_dot(doc1, doc2)

        denominator = math.sqrt(KMeans.calculate_dot(doc1, doc1) * KMeans.calculate_dot(doc2, doc2))

        if denominator:

            return float(numerator) / denominator

        else:

            return 0.0

    @staticmethod
    def calculate_dot(doc1, doc2):

        rst = 0.0

        for index, d in enumerate(doc1):

            rst += d * doc2[index]

        return rst

    @staticmethod
    def get_tf(sentence):
        """ 获取词频"""

        rst = {}

        words = re.split(';|；| ', sentence)

        for word in words:

            if word in rst:

                rst[word] += 1

            else:

                rst[word] = 1

        return rst

    @staticmethod
    def get_key_feature(keys):
        """ 获取topic 的特征信息 """

        rst = ''

        topics = re.split(';|；| ', keys)

        for topic in topics:

            if not topic:

                continue

            upper_concept = DBHandler.get_concept_by_relation(SQL.EXTEND_TOPIC.format(topic=topic), '1')

            if len(upper_concept):

                rst += upper_concept

                lower_concept = DBHandler.get_concept_by_relation(SQL.EXTEND_TOPIC.format(topic=topic), '2')

                if len(lower_concept):

                    rst += lower_concept
        return rst

    @staticmethod
    def method_sentence_extract(sentence):
        """ 抽取 固定格式中的词 """
        rst = ''

        if sentence:
            # 由于针对 . 有错误，故使用转义[.]
            parts = re.split(ur'[.]|,|;|；|，|。', sentence)

            for part in parts:

                if '提出' in part or 'propose' in part or '本文' in part or 'this paper' in part \
                    or '问题' in part or 'problem of' in part or '方法' in part or 'method' in part \
                        or '模型' in part or 'model' in part or '算法' in part or 'algorithm' in part:

                    rst += ' ' + part

        return rst
