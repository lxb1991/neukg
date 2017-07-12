# coding=utf-8
import MySQLdb
import threading
from DBUtils.PooledDB import PooledDB
from data import Const, BiData, PaperData, OntologyRelation, RelationList, GeneralRelation


class DBManager(object):
    """ 数据库连接管理 """

    __instance = None

    __pool = None

    __mutex = threading.Lock()

    def __new__(cls, *args, **kwargs):

        DBManager.__mutex.acquire()

        if not DBManager.__instance:

            print(' DBManager 实例 初始化')

            DBManager.__instance = object.__new__(cls, *args, **kwargs)

        DBManager.__mutex.release()

        return DBManager.__instance

    def __init__(self):

        DBManager.__mutex.acquire()  # 加锁 防止多次init

        if not DBManager.__instance.__pool:

            print(' DBManager 连接池 pool 初始化')

            self.__pool = PooledDB(creator=MySQLdb, mincached=2, maxcached=40, host='localhost', port=3306, user='root',
                                   passwd='lxb123456', db='textmining', charset='utf8')

        DBManager.__mutex.release()

    def query(self, sql, * is_dic):
        """ is_dic type: bool. 返回 cursor 是否需要使用 DictCursor """

        print('查询的sql为：%s' % sql)

        conn = self.__pool.connection()

        if is_dic:

            cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        else:

            cursor = conn.cursor()

        cursor.execute(sql)

        print('查询结果数量为：%d' % cursor.rowcount)

        result = cursor.fetchall()

        cursor.close()

        conn.close()

        return result


class SQL(Const):

    BI_TOPIC = "select distinct c_keys,e_keys,yea from computer where c_keys like '%{topic}%' order by yea desc"

    BI_TITLE = "select distinct c_title,e_title,yea from computer where c_title like '%{title}%' order by yea desc"

    PAPER = "select distinct * from computer where c_keys like '%{topic}%' or c_title like '%{topic}%' order by yea desc"

    SURVEY = "select * from computer where c_keys like '%{topic}%' or c_title like '%{topic}%'"

    RELATION = "select * from OntologyFullRelation where concept%s = '{topic}' order by confidence desc limit 0,10"

    RESEARCHER = "select * from computer where c_authors like '%{author}%'"

    AUTHOR_RELATION = "select * from computer where c_keys like '%{topic}%' or c_title like '%{topic}%' order by yea desc limit 0,50"

    HOT_RESEARCH = "select * from computer order by yea desc limit 0,50000"

    ONTOLOGY = "select c_keys from computer where yea ='1987' limit 0,500"

    ONTOLOGY_UNSUPERVISED = "select * from computer where c_keys like '%{topic}%' or c_title like '%{topic}%' "

    TOPIC = "select distinct * from computer where c_keys like '%{topic}%' or c_title like '%{topic}%'"

    EXTEND_TOPIC = "select * from OntologyFullRelation where concept%s = '{topic}' order by confidence desc limit 0,2"


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

                bi_dr = BiData(row[0], row[1])

                rst.append(bi_dr)

        return rst

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

            rc.co_occurrence = int(row['co_occurence'])

            rc.confidence = float(row['confidence'])

            gl = GeneralRelation()

            gl.tgt_concept = row['concept%s' % mark]

            gl.co_occurrence = rc.co_occurrence

            gl.confidence = rc.confidence

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
