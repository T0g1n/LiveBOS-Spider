# 序列函数：ABS_SERIALNO(变化参数)

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

序列函数：ABS\_SERIALNO(变化参数)

根据传入的变化参数对新增的记录信息计算序列。

l 变化参数：根据这个参数对系统表进行修改

例子：

在本例中，我们想按分钟变化对当前表进行新增记录操作

输入 ABS\_SERIALNO(ABS\_MINUTE($S))
