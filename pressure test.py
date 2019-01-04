import pymysql
import threading,time
class Deal_data(object):
    '''insert、select、update、delete data and primary key violation'''
    def __init__(self,host,port,user,passwd,db,tb):
        self.host=host
        self.user=user
        self.passwd=passwd
        self.port=port
        self.db=db
        self.tb=tb
    def connect_db(self,sql):
        conn=pymysql.connect(host=self.host,port=self.port,user=self.user,password=self.passwd,db=self.db,
                             charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
        cursor=conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        conn.close()
    def insert_data(self):
        for i in range(21):
            sql="insert into %s.%s (%s,%s,%s,%s) select %s,%s,%s,%s from %s.%s;"%(self.db,self.tb,'uname','password','date','money','uname','password','date','money',self.db,self.tb)
            Deal_data.connect_db(self,sql)
        print("插入数据完成")
    def select_data(self):
        sql="select * from %s.%s where id>2000000;"%(self.db,self.tb)
        Deal_data.connect_db(self, sql)
        print("查找数据完成")
    def update_data(self):
        sql="update %s.%s set password='123456' where id >2000000;"%(self.db,self.tb)
        Deal_data.connect_db(self, sql)
        print("更新数据完成")
    def delete_data(self):
        sql="delete from %s.%s where id>2000000;"%(self.db,self.tb)
        Deal_data.connect_db(self, sql)
        print("删除数据完成")
    def Primary_key_violation(self):
        sql="insert into %s.%s (id,uname,password,date,money) value (1,'','','','');"%(self.db,self.tb)
        try:
            Deal_data.connect_db(self, sql)
        except Exception as e:
            print(e)
class Deadlock(Deal_data):
    '''create deadlock'''
    def __init__(self,host,port,user,password,db,tb):
        super(Deadlock, self).__init__(host,port,user,password,db,tb)
    def transaction1(self):
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, db=self.db,
                                   charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
            cursor=conn.cursor()
            cursor.execute("start transaction;")
            cursor.execute("update %s.%s set password='123456' where id<200000;"%(self.db,self.tb))
            cursor.execute("update %s.%s set password='456789' where id>1500000;"%(self.db,self.tb))
            cursor.execute("commit;")
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)
    def transaction2(self):
        try:
            conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.passwd, db=self.db,
                                   charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
            cursor=conn.cursor()
            cursor.execute("start transaction;")
            cursor.execute("update %s.%s set password='111111' where id>1500000;" % (self.db,self.tb))
            cursor.execute("update %s.%s set password='222222' where id<200000;"%(self.db,self.tb))
            cursor.execute("commit;")
            cursor.close()
            conn.close()
        except Exception as e:
            print(e)

class Transfer_func(Deal_data):
    '''transfer functions'''
    def __init__(self,host,port,user,passwd,db,tb):
        super(Transfer_func, self).__init__(host,port,user,passwd,db,tb)
    def transfer_deadlock(self):
        trans_list=[]
        p_obj_list=[]
        Dl=Deadlock(self.host,self.port,self.user,self.passwd,self.db,self.tb)
        trans_list.append(Dl.transaction1)
        trans_list.append(Dl.transaction2)
        for i in trans_list:
            p=threading.Thread(target=i,)
            p.start()
            p_obj_list.append(p)
        for p in p_obj_list:
            p.join()
    def transfer_deal_data(self):
        dealdata=Deal_data(self.host,self.port,self.user,self.passwd,self.db,self.tb)
        dealdata.insert_data()
        dealdata.select_data()
        dealdata.update_data()
        dealdata.delete_data()
        dealdata.Primary_key_violation()

transfer=Transfer_func('192.168.5.10',3306,'root','Lw123456..+','acount','test')
transfer.transfer_deal_data()
transfer.transfer_deadlock()
