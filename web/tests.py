# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from DataEngine import common


# Create your tests here.
class MyTestCase(TestCase):

    def setUp(self):

        print('测试函数开始：')

    def test_encrypt(self):

        text = common.Encrypt.encrypt("多线程")

        print text

        print len(text)

        print common.Encrypt.decrypt(text)


    def tearDown(self):

        print('测试函数结束')