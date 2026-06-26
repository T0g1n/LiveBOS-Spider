# 获取属性：ABS_GETATTRIBUTE(属性名)

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

获取属性：ABS\_GETATTRIBUTE(属性名)

这个函数可以通过执行对象的属性名得到相对应的属性值 。

l 属性名：操作对象的属性名，LiveBOS
Studio将返回这个对象相应的属性值。

l 例子： 本例想获得对象"apex"的属性值：

var array = ABS\_GETATTRIBUTE("apex")
