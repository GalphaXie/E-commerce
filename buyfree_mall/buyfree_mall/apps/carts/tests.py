from django.test import TestCase

# Create your tests here.

"""
购物车:
登录-->购物车数据保存到哪里?
为何选redis? 为何用 hash和set? hash的k:v如何设计? (hash->商品id:数量; set->是否勾选) 

未登录-->购物车数据保存到哪里?
为何cookie?
    - 1.不用担心跨站请求伪造(因为跨站请求伪造是利用cookie中的用户身份信息,伪造的是用户身份;但是这里用户尚未登录,不存在用户信息)
    - 2.方便通过cookie传递到后端,cookie是会由浏览器自动携带,不需要主动去操作传递.
cookie存在的问题:  cookie保存的是字符串,但是用户购物车信息相对较多,维护字典格式->cookie需要的字符串(即使用有格式的json),但是json转化的效率很低
    - 直接保存数据二进制的状态 --> 程序的解决方案: pickle

关于json和pickle选择问题:
    - json 跨语言  而  pickle 是Python独有;  如果不存在跨语言(如python->js->html等等)
    - pickle.dumps()   和    pickle.loads()    

编码|解码:  base64
base64 -> 2**6 = 64 (6个2进制数即0-1为一组, 用64个可打印的字符: a-z,A-Z,0-9 = 26+26+10+2=62+2个根据不同操作系统而不同的字符)
    - 1. 好像位数不够的时候用'=',所以会看到编码后字符串中出现 '='
    - 2. 编码之后仍然是 byte 字节,有时候还需要再通过python的decode方法进一步转化成str; 不过这里不需要

'类比'穿|脱袜子和鞋子
    
--------------------------------------------
保存购物车(新增商品和数量)

存在问题: response = Response()  response.set_cookie   => 在序列化器取不到 response 对象,只能取到 request 对象

redis 特性:
1. 存入数据不论什么类型,redis客户端存入服务器后都是 str
2. 取出数据都是 bytes 类型

补充: int(sku_id) => bytes 直接 转成 int
- mysql数据库查询 不需要 关注 类型 , 内部自动处理
- python 的字典 的 key 需要关注

删除: 
post put patch delete 都可以 有请求体

------------------------------------------------------------------
幂等性:
- 对于相同的请求,多次请求的结果和一次请求的结果始终相同,称之为 幂等性 (关键字:请求,结果相同)















"""