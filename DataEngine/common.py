# coding=utf-8
import re
import base64


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


class Encrypt(object):

    mix_value = {
        'A': 'J', 'J': 'A', 'S': '3', '3': 'S',
        'B': 'K', 'K': 'B', 'T': '4', '4': 'T',
        'C': 'L', 'L': 'C', 'U': '5', '5': 'U',
        'D': 'M', 'M': 'D', 'V': '6', '6': 'V',
        'E': 'N', 'N': 'E', 'W': '7', '7': 'W',
        'F': 'O', 'O': 'F', 'X': 'G',
        'G': 'X', 'P': 'Y', 'Y': 'P',
        'H': 'Q', 'Q': 'H', 'Z': 'I',
        'I': 'Z', 'R': '2', '2': 'R',
        }

    @staticmethod
    def encrypt(text):

        source = base64.encodestring(text)

        return Encrypt.mix(source).replace('\n', '')

    @staticmethod
    def decrypt(text):

        target = Encrypt.regain(text)

        return base64.decodestring(target)

    @staticmethod
    def mix(text):

        target = list(text)

        for index, t in enumerate(target):

            if t in Encrypt.mix_value:

                target[index] = Encrypt.mix_value[t]

        return "".join(target)

    @staticmethod
    def regain(text):

        return Encrypt.mix(text)
