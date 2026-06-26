# 日期、时间格式函数：ABS_DATESTRING(日期字串、格式)

> LiveBOS Studio > 概念手册 > 高级开发 > 函数说明

---

日期、时间格式函数：ABS\_DATESTRING(日期字串、格式)

日期和时间格式由日期和时间格式字符串指定。在日期和时间格式字符串中，未加引号的字母 'A' 到 'Z' 和 'a' 到
'z' 被解释为格式字母，用来表示日期或时间字符串元素。文本可以使用单引号 (') 引起来，以免进行解释。"''" 表示单引号。所有其他字符均不解释；只是在格式化时将它们简单复制到输出字符串，或者在分析时与输入字符串进行匹配。

定义了以下格式字母（所有其他字符 'A' 到 'Z' 和 'a' 到 'z' 都被保留）：

|  |  |  |  |
| --- | --- | --- | --- |
| **字母** | **日期或时间元素** | **表示** | **示例** |
| G | Era 标志符 | [Text](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#text) | AD |
| y | 年 | [Year](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#year) | 1996; 96 |
| M | 年中的月份 | [Month](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#month) | July; Jul; 07 |
| w | 年中的周数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 27 |
| W | 月份中的周数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 2 |
| D | 年中的天数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 189 |
| d | 月份中的天数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 10 |
| F | 月份中的星期 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 2 |
| E | 星期中的天数 | [Text](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#text) | Tuesday; Tue |
| a | Am/pm 标记 | [Text](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#text) | PM |
| H | 一天中的小时数（0-23） | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 0 |
| k | 一天中的小时数（1-24） | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 24 |
| K | am/pm 中的小时数（0-11） | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 0 |
| h | am/pm 中的小时数（1-12） | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 12 |
| m | 小时中的分钟数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 30 |
| s | 分钟中的秒数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 55 |
| S | 毫秒数 | [Number](mk:@MSITStore:F:\Downloads\Document\Java_api.chm::/java/text/SimpleDateFormat.html#number) | 978 |

图6.8.4.1

格式字母通常是重复的，其数量确定其精确表示： **Text:** 对于格式化来说，如果格式字母的数量大于或等于 4，则使用完全形式；否则，在可用的情况下使用短形式或缩写形式。对于分析来说，两种形式都是可接受的，与格式字母的数量无关。

**Number:** 对于格式化来说，格式字母的数量是最小的数位，如果数位不够，则用
0 填充以达到此数量。对于分析来说，格式字母的数量被忽略，除非必须分开两个相邻字段。

**Year:** 对于格式化来说，如果格式字母的数量为2，则年份截取为 2 位数,否则将年份解释为number。对于分析来说，如果格式字母的数量大于
2，则年份照字面意义进行解释，而不管数位是多少。因此使用格式"MM/dd/yyyy"，将 "01/11/12" 分析为公元
12 年 1 月 11 日。在分析缩写年份格式（"y" 或 "yy"）时，必须相对于某个世纪来解释缩写的年份。

**Month:** 如果格式字母的数量为 3 或大于 3，则将月份解释为text；否则解释为number。

示例：

给定的日期和时间为中国太平洋时区的本地时间 2001-07- 04 12:08:56。

|  |  |
| --- | --- |
| "yyyy-MM-dd'T'HH:mm:ss.SSSZ" | 2001-07-04T12:08:56.235-0700 |

图6.8.4.2
