# JAVA对象函数：ABS_LOADBEAN(javabean名称)

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

JAVA对象函数：ABS\_LOADBEAN(javabean名称)

这个函数加载一个javabean。

l javabean名称：想使用的JAVA类的具体描述

l 例子： 如果想使用自定义的javabean：com.apex.text.Employe 它有属性name及方法pay，则可以像如下方式使用。牋

var
v=ABS\_LOADBEAN("com.apex.text.Employe")

v.setName($);

v.pay();
