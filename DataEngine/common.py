# coding=utf-8
import re


class Convert(object):
    """ 把 paper 信息 转化为 其他类信息"""

    @staticmethod
    def str2list(m_str, m_list, capacity):

        if m_str:

            datas = re.split(';|；', m_str)

            for data in datas:

                if len(m_list) > capacity:

                    return

                if len(data.strip()) and data not in m_list:

                    m_list.append(data)
