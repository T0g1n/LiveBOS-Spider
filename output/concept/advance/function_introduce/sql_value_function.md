# SQL值函数：ABS_SQLVALUE(SQL语句,[参数1,参数2,

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

SQL值函数：ABS\_SQLVALUE(SQL语句,[参数1,参数2,...])

这个函数可以执行一条由用户自定义参数的SQL语句

l SQL语句：用户想执行的SQL语句

l 参数1：用户自定义准备用于SQL语句中的参数。

例子：本例想执行一条选择语句，并准备使用"人名"这个参数

ABS\_SQLVALUE("select ?",[$F])
