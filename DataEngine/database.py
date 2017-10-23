# coding=utf-8
import MySQLdb
import threading
from DBUtils.PooledDB import PooledDB
from data import Const, PaperData, OntologyRelation, RelationList, GeneralRelation, BiData, CrowdData
import logging


logger = logging.getLogger('pixiu')


class DBManager(object):
    """ 数据库连接管理 """

    __instance = None

    __pool = None

    __mutex = threading.Lock()

    def __new__(cls, *args, **kwargs):

        DBManager.__mutex.acquire()

        if not DBManager.__instance:

            logger.info(' DBManager 实例 初始化')

            DBManager.__instance = object.__new__(cls, *args, **kwargs)

        DBManager.__mutex.release()

        return DBManager.__instance

    def __init__(self):

        DBManager.__mutex.acquire()  # 加锁 防止多次init

        if not DBManager.__instance.__pool:

            logger.info(' DBManager 连接池 pool 初始化')

            self.__pool = PooledDB(creator=MySQLdb, mincached=2, maxcached=40, host='localhost', port=3306, user='root',
                                   passwd='lxb123456', db='textmining', charset='utf8')

        DBManager.__mutex.release()

    def query(self, sql, * is_dic):
        """ is_dic type: bool. 返回 cursor 是否需要使用 DictCursor """

        logger.info('查询的sql为：%s' % sql)

        conn = self.__pool.connection()

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

    def save(self, sql):

        logger.info('存储sql：%s' % sql)

        conn = self.__pool.connection()

        cursor = conn.cursor()

        cursor.execute(sql)

        conn.commit()

        cursor.close()

        conn.close()


class SQL(Const):

    RELATION = "select * from OntologyFullRelation where concept%s = '{topic}' order by confidence desc limit 0,10"

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

        results = DBManager().query(sql)

        for row in results:

            if row[0] and row[0].strip() != '':

                rst.append(row[0])

        return rst

    @staticmethod
    def get_bi_data(sql):

        rst = []

        results = DBManager().query(sql)

        for row in results:

            if (row[0] and row[0].strip() != '') and (row[1] and row[1].strip() != ''):

                bi_dr = BiData()

                bi_dr.bi_cn = row[0]

                bi_dr.bi_en = row[1]

                rst.append(bi_dr)

        return rst

    @staticmethod
    def get_single_bi_data(sql):

        results = DBManager().query(sql)

        if results:

            return results[0]

        else:

            return None, None

    @staticmethod
    def get_paper_data(sql):

        rst = []

        results = DBManager().query(sql, True)

        for row in results:

            paper_data = PaperData(c_title=row['c_title'], e_title=row['e_title'], c_authors=row['c_authors'],
                                   e_authors=row['e_authors'], c_keys=row['c_keys'], e_keys=row['e_keys'],
                                   c_abs=row['c_abs'], e_abs=row['e_abs'], c_org=row['c_org'], e_org=row['e_org'],
                                   c_journal=row['c_jour'], e_journal=row['e_jour'], doi=row['doi'], year=row['yea'])

            rst.append(paper_data)

        return rst

    @staticmethod
    def get_relation(sql, mark):

        if mark == '1':

            sql = (sql % '2')

        else:

            sql = (sql % '1')

        rst_relation = OntologyRelation()

        results = DBManager().query(sql, True)

        for row in results:

            rc = RelationList()

            rc.tgt_concept = row['concept%s' % mark]

            gl = GeneralRelation()

            gl.tgt_concept = row['concept%s' % mark]

            rl_rst = ''

            dot_mark = 0  # 是否需要加顿号

            if row['e_relation'] == "E":

                rst_relation.e_list.append(rc)

                rl_rst += '等价关系'

                dot_mark += 1

            if row['h_relation'] == "H":

                rst_relation.h_list.append(rc)

                if dot_mark >= 1:

                    rl_rst += '、'

                rl_rst += '层次关系'

                dot_mark += 1

            if row['s_relation'] == "S":

                rst_relation.s_list.append(rc)

                if dot_mark >= 1:

                    rl_rst += '、'

                rl_rst += '子类关系'

                dot_mark += 1

            if row['m_relation'] == "M":

                rst_relation.m_list.append(rc)

                if dot_mark >= 1:

                    rl_rst += '、'

                rl_rst += '部分关系'

                dot_mark += 1

            if row['i_relation'] == "I":

                rst_relation.i_list.append(rc)

                if dot_mark >= 1:

                    rl_rst += '、'

                rl_rst += '实例关系'

                dot_mark += 1

            gl.relations = rl_rst

            rst_relation.g_list.append(gl)

        return rst_relation

    @staticmethod
    def get_concept_by_relation(sql, mark):

        rst = ''

        if mark == '1':

            sql = (sql % '2')

        else:

            sql = (sql % '1')

        results = DBManager().query(sql, True)

        for row in results:

            rst += row['concept%s' % mark] + '# '

        return rst

    @staticmethod
    def save_crowd_data(sql):

        DBManager().save(sql)

    @staticmethod
    def get_crowd_data(sql):

        rst = []

        results = DBManager().query(sql, True)

        for row in results:

            data = CrowdData()

            data.author = row['author']

            data.key = row['research']

            data.org = row['org']

            data.journal = row['journal']

            rst.append(data)

        return rst
