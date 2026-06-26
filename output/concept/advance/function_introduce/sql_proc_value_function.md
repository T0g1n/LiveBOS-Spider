# SQL过程值函数：ABS_SQLPROCVALUE(SQL语句,[参数1,参数2,

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

SQL过程值函数：ABS\_SQLPROCVALUE(SQL语句,[参数1,参数2,...])

这个函数把参数放入一个存储过程中以备将来使用。

l SQL语句：这时候的SQL语句是一个存储过程

l 参数1：准备放入存储过程中的参数

l 例子：本例想把"人名""ID"这两个参数传入存储体sp\_test中

ABS\_SQLPROCVALUE("sp\_test
?,?,?",[$F,$F])
