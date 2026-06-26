# SQL结果集函数：LB_sqlResultSet(SQL语句,[参数1,参数2,

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

SQL结果集函数：LB\_sqlResultSet(SQL语句,[参数1,参数2,...])

这个函数可以执行由用户自定义参数的SQL语句的结果集 。

l SQL语句：用户输入的可执行的SQL语句

l 参数：用户在设置SQL语句的过程中可能用到的参数

l 例子：从tUser表中获得用户ID和名字

var rs= LB\_sqlResultSet("select
userId,name from tUser",[]); While(rs.next())
