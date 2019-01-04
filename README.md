# 数据库压测脚本
## 实现的功能：
1. 创建一个大表
2. 多行的增删改查
3. 主键冲突
4. 产生死锁
## 代码描述：
1. Create_data创建表结构，插入少量的数据
2. Deal_data类定义了数据库连接方法，实现了增删改查和主键冲突的功能
3. Deadlock类继承Deal_data,实现了两个事务并发修改数据造成死锁
4. Transfer_func对Deal_data,Deadlock实例化调用
5. 实例化Transfer_func，传入数据库相关的数据
## 表结构：
> CREATE TABLE `test` (
>  `id` int(11) NOT NULL AUTO_INCREMENT,
>  `uname` varchar(32) NOT NULL,
>  `password` varchar(64) NOT NULL,
>  `date` date NOT NULL,
>  `money` float DEFAULT NULL,
>  PRIMARY KEY (`id`)
> ) ENGINE=InnoDB AUTO_INCREMENT=6684557 DEFAULT CHARSET=utf8; 
