import pymysql
import threading
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float
from sqlalchemy.orm import sessionmaker


class Create_table(object):
    '''create table  structure and insert data'''

    def __init__(self, host, port, user, passwd, db,tb):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.db = db
        self.tb = tb

    def create_table(self):
        engine = create_engine("mysql+pymysql://%s:%s@%s:%s/%s" % (self.user, self.passwd, self.host, self.port, self.db),
                               encoding='utf-8', echo=True)
        Base = declarative_base()  # 生成orm基类

        class Test(Base):
            __tablename__ = self.tb  # 表名
            id = Column(Integer, primary_key=True, autoincrement=True)
            uname = Column(String(32))
            password = Column(String(64))
            date = Column(Date)
            money = Column(Float)

        Base.metadata.create_all(engine)  # 创建表结构
        return self.insert_data(engine, Test)

    def insert_data(self, engine, Test):
        Session_class = sessionmaker(bind=engine)  # 创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
        Session = Session_class()  # 生成session实例
        test_obj1 = Test(uname='guanyu', password='123456', date='2019-01-04', money=250)
        test_obj2 = Test(uname='zhangfei', password='258369', date='2019-11-14', money=25847.2)
        test_obj3 = Test(uname='liubei', password='666666', date='2019-06-06', money=666.666)
        Session.add_all([test_obj1, test_obj2, test_obj3])
        Session.commit()


class Deal_data(object):
    '''INSERT...SELECT...、SELECT、UPDATE、DELETE data and primary key violation'''

    def __init__(self, host, port, user, passwd, db, tb, num):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.db = db
        self.tb = tb
        self.num = num

    def connect_db(self, sql):
        conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, db=self.db,
                               charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()

    def insert_manydata(self):
        for i in range(self.num):
            sql = "insert into %s.%s (%s,%s,%s,%s) select %s,%s,%s,%s from %s.%s;" % (
            self.db, self.tb, 'uname', 'password', 'date', 'money', 'uname', 'password', 'date', 'money', self.db,
            self.tb)
            Deal_data.connect_db(self, sql)
        print("插入数据完成")

    def select_data(self):
        sql = "select * from %s.%s where id>2000000;" % (self.db, self.tb)
        Deal_data.connect_db(self, sql)
        print("查找数据完成")

    def update_data(self):
        sql = "update %s.%s set password='123456' where id >2000000;" % (self.db, self.tb)
        Deal_data.connect_db(self, sql)
        print("更新数据完成")

    def delete_data(self):
        sql = "delete from %s.%s where id>2000000;" % (self.db, self.tb)
        Deal_data.connect_db(self, sql)
        print("删除数据完成")

    def Primary_key_violation(self):
        sql = "insert into %s.%s (id,uname,password,date,money) value (1,'','','2019-12-25',666);" % (self.db, self.tb)
        try:
            Deal_data.connect_db(self, sql)
        except Exception as e:
            print(e)


class Deadlock(Deal_data):
    '''create deadlock'''

    def __init__(self, host, port, user, password, db, tb, num):
        super(Deadlock, self).__init__(host, port, user, password, db, tb, num)

    def transaction1(self):
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, db=self.db,
                                   charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
            cursor = conn.cursor()
            cursor.execute("start transaction;")
            cursor.execute("update %s.%s set password='123456' where id<200000;" % (self.db, self.tb))
            cursor.execute("update %s.%s set password='456789' where id>1500000;" % (self.db, self.tb))
            cursor.execute("commit;")
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

    def transaction2(self):
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, db=self.db,
                                   charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
            cursor = conn.cursor()
            cursor.execute("start transaction;")
            cursor.execute("update %s.%s set password='111111' where id>1500000;" % (self.db, self.tb))
            cursor.execute("update %s.%s set password='222222' where id<200000;" % (self.db, self.tb))
            cursor.execute("commit;")
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)


class Transfer_func(Deal_data):
    '''transfer Create_table Deal_data Deadlock'''

    def __init__(self, host, port, user, passwd, db, tb,num):
        super(Transfer_func, self).__init__(host, port, user, passwd, db, tb,num)

    def transfer_deadlock(self):
        trans_list = []
        p_obj_list = []
        Dl = Deadlock(self.host, self.port, self.user, self.passwd, self.db, self.tb, self.num)
        trans_list.append(Dl.transaction1)
        trans_list.append(Dl.transaction2)
        for i in trans_list:
            p = threading.Thread(target=i, )
            p.start()
            p_obj_list.append(p)
        for p in p_obj_list:
            p.join()

    def transfer_deal_data(self):
        C = Create_table(self.host, self.port, self.user, self.passwd, self.db, self.tb)
        C.create_table()
        dealdata = Deal_data(self.host, self.port, self.user, self.passwd, self.db, self.tb, self.num)
        dealdata.insert_manydata()
        dealdata.select_data()
        dealdata.update_data()
        dealdata.delete_data()
        dealdata.Primary_key_violation()

    def transfer_clear_data(self):
        confirm = input("are you truncate and drop table? Y|N:")
        if confirm == 'Y' or confirm == 'Y'.lower():
            sql = "truncate table %s" % self.tb
            sql1 = "drop table %s" % self.tb
            dealdata = Deal_data(self.host, self.port, self.user, self.passwd, self.db, self.tb, self.num)
            dealdata.connect_db(sql)
            dealdata.connect_db(sql1)
        elif confirm == 'N' or confirm == 'N'.lower():
            pass
        else:
            return "input error"


host = input("输入压测的实例ip：")
port = int(input("输入压测的实例port："))
user = input("输入压测的实例用户：")
passwd = input("输入压测的实例用户密码：")
db = input("输入压测实例的库名：")
tb = input("输入db内需要创建的表名：")
num = int(input("创建多少数据的量级："))    #3（原本有三条数据），num=3(表中的数据循环插入三遍),all=3*2^3

transfer = Transfer_func(host,port,user,passwd,db,tb,num)
transfer.transfer_deal_data()
transfer.transfer_deadlock()
transfer.transfer_clear_data()
