# 设置属性：ABS_SETATTRIBUTE(属性名,属性值)

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

设置属性：ABS\_SETATTRIBUTE(属性名,属性值)

这个函数可以为用户自定义的属性名称赋值。

l 属性名：用户自定义的属性名称

l 属性值：用户想要为自定义属性赋予的值

l 例子： 本例想自定义一个数组array，并把它命名为"apex"

array
:= new Array(); ABS\_SETATTRIBUTE("apex",array);
