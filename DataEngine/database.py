# coding=utf-8
import MySQLdb
from DBUtils.PooledDB import PooledDB
from data import Const, PaperData, OntologyRelation, GeneralRelation, BiData, CrowdData
import logging


logger = logging.getLogger('pixiu')

logger.info("初始化->数据库实例")

__pool = PooledDB(creator=MySQLdb, mincached=2, maxcached=40, host='localhost', port=3306, user='root',
                                   passwd='lxb123456', db='textmining', charset='utf8')


def query(sql, * is_dic):
    """ is_dic type: bool. 返回 cursor 是否需要使用 DictCursor """

    logger.info('查询的sql为：%s' % sql)

    conn = __pool.connection()

    if is_dic:

        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    else:

        cursor = conn.cursor()

    cursor.execute(sql)

    logger.info('查询结果数量为：%d' % cursor.rowcount)

    result = cursor.fetchall()

    cursor.close()

    conn.close()

    return result


def save(sql):

    logger.info('存储sql：%s' % sql)

    conn = __pool.connection()

    cursor = conn.cursor()

    cursor.execute(sql)

    conn.commit()

    cursor.close()

    conn.close()


class SQL(Const):

    RELATION = "select * from ontologyfullrelation where concept%s = '{topic}' order by confidence desc limit 0,10"

    BI_SINGLE_TOPIC = "select ckey,ekey from bikey where ckey = '{key}' or ekey = '{key}'"

    BI_TOPIC = "select distinct c_keys,e_keys,yea from computer where c_keys like '%{topic}%' or e_keys like '%{topic}%' order by yea desc"

    RESEARCHER = "select distinct * from computer where c_authors like '%{name}%' or e_authors like '%{name}%'"

    PAPER = "select distinct * from computer where c_keys like '%{topic}%' or e_keys like '%{topic}%' order by yea desc"

    MORE_PAPER = "select distinct * from computer where c_keys like '%{topic}%' or e_keys like '%{topic}%' " \
                 "or c_authors like '%{topic}%' or e_authors like '%{topic}%' order by yea desc"

    SAVE_UNCHECKED = "insert into uncheck(author, org, research, journal)values('{author}','{org}','{key}','{journal}')"

    UNCHECKED = "select * from uncheck"


class DBHandler:
    """ 数据库辅助查询 """

    def __init__(self):
        pass

    @staticmethod
    def get_keys(sql):

        rst = []

        results = query(sql)

        for row in results:

            if row[0] and row[0].strip() != '':

                rst.append(row[0])

        return rst

    @staticmethod
    def get_bi_data(sql):

        rst = []

        results = query(sql)

        for row in results:

            if (row[0] and row[0].strip() != '') and (row[1] and row[1].strip() != ''):

                bi_dr = BiData()

                bi_dr.bi_cn = row[0]

                bi_dr.bi_en = row[1]

                rst.append(bi_dr)

        return rst

    @staticmethod
    def get_single_bi_data(sql):

        results = query(sql)

        if results:

            return results[0]

        else:

            return None, None

    @staticmethod
    def get_paper_data(sql):

        rst = []

        results = query(sql, True)

        for row in results:

            paper_data = PaperData(c_title=row['c_title'], e_title=row['e_title'], c_authors=row['c_authors'],
                                   e_authors=row['e_authors'], c_keys=row['c_keys'], e_keys=row['e_keys'],
                                   c_abs=row['c_abs'], e_abs=row['e_abs'], c_org=row['c_org'], e_org=row['e_org'],
                                   c_journal=row['c_jour'], e_journal=row['e_jour'], doi=row['doi'], year=row['yea'])

            if (paper_data.c_keys and "/" in paper_data.c_keys) or (paper_data.e_keys and "/" in paper_data.e_keys):

                continue

            rst.append(paper_data)

        return rst

    @staticmethod
    def get_relation(sql, mark):

        if mark == '1':

            sql = (sql % '2')

        else:

            sql = (sql % '1')

        rst_relation = OntologyRelation()

        results = query(sql, True)

        for row in results:

            gl = GeneralRelation()

            gl.tgt_concept = row['concept%s' % mark]

            if gl.tgt_concept and "/" in gl.tgt_concept:

                continue

            rst_relation.g_list.append(gl)

        return rst_relation

    @staticmethod
    def get_concept_by_relation(sql, mark):

        rst = ''

        if mark == '1':

            sql = (sql % '2')

        else:

            sql = (sql % '1')

        results = query(sql, True)

        for row in results:

            rst += row['concept%s' % mark] + '# '

        return rst

    @staticmethod
    def save_crowd_data(sql):

        save(sql)

    @staticmethod
    def get_crowd_data(sql):

        rst = []

        results = query(sql, True)

        for row in results:

            data = CrowdData()

            data.author = row['author']

            data.key = row['research']

            data.org = row['org']

            data.journal = row['journal']

            rst.append(data)

        return rst
