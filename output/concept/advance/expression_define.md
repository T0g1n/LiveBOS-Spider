# 

> LiveBOS Studio > 概念手册 > 高级开发

---

## 表达式定义

### 1.1.1.表达式语言申明

#### 系统默认语言

表达式的默认脚本语言。例如可通过配置system.script.language=javascript，表示脚本语言与javascript语法一致。

#### 指定语言

在表达式中可以指定此脚本使用的语言，如：

<%@ livebos
language="javascript" %>

### 1.1.2.SQL表达式定义

LiveBOS3.0之前SQL的表达式语法,是通过在SQL语句中直接嵌入宏的方式来实现.如F1=$VP
等.

从3.0开始,SQL表达式的语法进行了改进.在SQL语句中需要进行计算或替换的地方用,.. 来表示, 其中0..n代表参数位置.如F1=。然后针对,..进行表达式设计，LiveBOS计算表达式的值，然后将替换成对应值,默认是原样替换,可以通过给表达式指定目标类型,LiveBOS将根据目标类型对表达式值进行处理,如目标为字符串,则加入’’,并对值中出现的引号进行转义,如目标为日期型,将根据数据库类型转换成convert或to\_date之类的函数。

### 1.1.3.引用定义

#### 属性

##### 对象属性

表6.1

|  |  |  |  |
| --- | --- | --- | --- |
| 属性名 | 说明 | 类型 | 注释 |
| **objectName** | 对象名称 | 字符型 |  |
| **objectTable** | 对象表名 | 字符型 |  |
| **operate** | 当前操作类型 | 数值型 | 0:查看,1:新增,2:修改,3:删除 |
| **isInsert** | 是否为新增操作 | 布尔型 |  |
| **isUpdate** | 是否为修改操作 | 布尔型 |  |
| **isDelete** | 是否为删除操作 | 布尔型 |  |
| **parameter** | 查询参数 | 对象变量 | 对象视图,虚拟对象等类型的查询参数 |

##### 字段属性

表6.2

|  |  |  |  |
| --- | --- | --- | --- |
| 属性名 | 说明 | 类型 | 注释 |
| **sqlName** | 查询的SQL字段名 | 字符型 | ,一般为对象表名.字段代码,如果是父对象字段,则为父对象表名.字段代码. |
| **displayValue** | 字段的显示值 | 字符型 | 取字段的显示值,如当字段类型为选择项时,则为选择项的说明值.为多值选项时,则为“选项1说明|选项2说明 ” |

##### 表格字段属性

表6.3

|  |  |  |  |
| --- | --- | --- | --- |
| 属性名 | 说明 | 类型 | 注释 |
| **count** | 记录数 | 数值型 |  |
| **isEmpty** | 表格是否为空 | 布尔型 |  |
| **parent** | 表格的主体 | 对象型 |  |

##### 工作流属性

表6.4

|  |  |  |  |
| --- | --- | --- | --- |
| 属性名 | 说明 | 类型 | 注释 |
| **initiator** | 流程发起人 | 字符型 |  |
| **owner** | 当前执行人 | 字符型 |  |

#### 内置变量

##### 对象自身

变量名为O\_THIS。O\_THIS可忽略,如O\_THIS.F1
等同于 F1。

##### 操作主体对象

变量名为O\_MASTER。在对象流程或方法定义中引用操作的主体对象。

##### 操作参数对象

变量名为O\_PARAMETER。在对象流程或方法定义中引用操作的参数。

##### 工作流对象

变量名为O\_WORKFLOW。O\_WORKFLOW.XXX
方式引用工作流表单的值、工作流定义的变量及属性.其XXX为流程表单字段名、流程变量名或属性值。

#### 系统参数

##### 登录相关类$Login

登录用户：$Login.User

登录IP：$Login.IP

登录时间：$Login.Time

登录用户用户属性：$Login.User.XXX

登录用户对应关联对象：$Login.User.#关联对象@关联字段

##### 时间类型$DateTime

当日：$DateTime.Today

上一天：$DateTime.Yesterday

本周几：$DateTime.Week.NAME，如$DateTime.Week.MON
…

上周几：$DateTime.LastWeek.NAME，如$DateTime.LastWeek.SUN
…

当月初：$DateTime.Month.Begin

当月末：$DateTime.Month.End

上月初：$DateTime.LastMonth.Begin

上月末：$DateTime.LastMonth.End

年初：$DateTime.Year.Begin

年末：$DateTime.Year.End

上年初：$DateTime.LastYear.Begin

上年末：$DateTime.LastYear.End

当前时间：$DateTime.Now

记录创建时间：$DateTime.Timestamp.Create

记录更新时间：$DateTime.Timestamp.Update

##### 应用类型$App

SQL返回值：$App.RETCODE

SQL返回说明：$App.RETNOTE

对象流程返回值：$App.BIZCODE

对象流程返回说明：$App.BIZNOTE

自定义SQL型及JAVABEAN参数：$App.参数名

### 1.1.4.宏定义

3.2以后版本取消宏定义，均用“引用定义”代替

#### 字段

$F
: 代表引用当前对象的字段XXX

$F:
用于对象操作，表示引用主体对象（TTT）的字段XXX

$HY:
对象引用其表格字段FF1中的FF2值

$HYB
:引用其表格字段FF1中的FF2的聚合值

XXX值说明：

SUM--
合计

AVG
-- 平均值

MAX
-- 最大值

MIN
-- 最小值

COUNT
-- 记录数

#### 关系对象字段

$R
: 代表引用当前对象的内部对象类型字段FFF中字段XXX的值。

#### 关联对象字段

$B,$B
: 代表引用关联对象TTT中字段FFF2的值或聚合值。其中FFF1代表关联对象TTT引用当前对象的字段。

XXX值说明：

NEW
-关联对象TTT.FFF2的新增对象的值

CHANGE
- TTT.FFF2的改变值

SUM-
TTT.FFF2的合计值

AVG
-- 平均值

MAX
- 最大值

MIN
-- 最小值

COUNT
-- 记录数

#### 系统参数

$S,$
: 引用系统参数，可引用的系统参数：

$S ：当前登录用户ID

$S：当前用户登录IP

$
：登录用户中对应tUser表中的字段XXX值

$S
：登录用户中对应tUser关联定义表XXX（由系统参数user.relative.table配置的表）的ID或自定义登录主键的值。如员工信息表（tEmploye）与tUser一一对应时，需要取当前用户的员工对应ID值，则可以使用$S

$S
：当日

$S
：当前时间

$S：当前对象名

$S：当前对象表名

$S ：创建

$S ：更新时间

$SV
: 系统参数变量,可引用系统参数中SQL型变量的值,XXX代表参数名或者用户定义的javabean类型系统参数变量并在参数变量中声明的参数名。

一些固定值 :

$SV: 空值

$SV : 消息确认对话框返回值

$SV
: SQL返回值

$SV:
SQL返回说明

$SV
：当天

$SV
：上一天

$SV:
本周一

$SV:本周日

$SV:上周一

$SV:上周日

$SV:当月初

$SV:当月末

$SV:上月初

$SV:上月末

$SV:年初

$SV:年末

$SV:上年初

$SV:上年末

#### 系统变量

@
:引用系统变量值,可以通过对@的赋值操作改变变量值,并在该变量声明的生命周期中起作用.

#### 表格字段

$HYM:表格对象引用其主对象XXX字段值。

#### 操作参数

$V:引用操作参数PPP的值

$VR
:引用操作参数PPP中字段XXX的值

$MP:
引用操作主体的视图参数或查询参数PPP值

$OV:
引用当前操作的一些变量,

$OV:当前对象的操作类型 1:新增,2:修改,3:删除$OV:当前操作序列号,批量操作每次调用操作主体时其序列号会加一.

#### 流程参数

$WF
: 工作流操作中引用工作流表TTT字段XXX值

$WFR
: 工作流操作中引用工作流表TTT字段FF内部对象XX值

$WFP
: 流程用户参数

$WFP:流程发起人

$WFP:活动执行人

$WFS:
工作流操作中引用子流程在子流程表单TTT的字段XXX的值,在子流程调用活动中有效

#### 视图参数

$VP
: 对象引用其视图参数或查询参数XXX值

#### 对象聚合变量

$OAV:引用对象TTT中字段FFF的聚合值。

XXX值说明：

SUM-
计值

AVG
-- 平均值

MAX
- 最大值

MIN
-- 最小值

COUNT
-- 记录数

#### 条件搜索变量

$FP
: 对象条件搜索时引用输入的条件变量XXX值。
