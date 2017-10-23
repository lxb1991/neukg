# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from DataEngine import engine
from DataEngine.data import PaperData


# Create your tests here.
class MyTestCase(TestCase):

    def setUp(self):

        print('测试函数开始：')

    def test_researcher(self):

        data = engine.get_info_researcher("任飞亮")

        for org in data.organizations:

            print('--->' + org)

        for topic in data.topics:

            print('===>' + topic)

        for researcher in data.researchers:

            print('+++>' + researcher)

    def test_topic(self):

        data = engine.get_info_topic("动态规划")

        for cn in data.bilingual_cn:

            print("cn -->" + cn)

        for en in data.bilingual_en:

            print("en ===>" + en)

        for con1 in data.topics_upper:

            print("+++>" + con1)

        for con2 in data.topics_lower:

            print("~~~~>" + con2)

    def test_bilingual(self):

        data = engine.get_more_bilingual("动态规划")

        print("数量：%d"%len(data))

        print(data[0].bi_cn + "---->" + data[0].bi_en)

        paper = engine.get_more_paper("机器学习")

        print("数量：%d"%len(paper))

    def test_save(self):

        paper = PaperData("1", "2", "3", "4", "5", "6", "7",
                          "8", "9", "10", "11", "12", "13", "14")

        engine.save_crowd_data(paper)

    def tearDown(self):

        print('测试函数结束')