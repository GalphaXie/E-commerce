from django.test import TestCase

# Create your tests here.

# 情况: 1.第一次使用qq登录,商城有账号; 2.qq有账号,但是第一次登录商城账号;
''''
QQ身份:openid()  - 绑定 本地model.User

前置工作: 注册成为 开发者 +  域名 备案

情况: 组合成　４种　
是否第一次登录ＱＱ：　①是　　②否
是否注册过商城：　③是　　④否


url拼接:

# 为何code和access_token不同时返回?
- 前面用户登录表示 用户 认可'QQ'作为安全的三方;
- 然后后面商城发送code 表示 商城认可 'QQ'作为安全的三方;
- 他们都需要通过三方来建立信任．

OAuth 开放认证标准 -- 两步: 1.(一套系统)判断要使用接口人的身份是什么; 2.(另一套系统功能)提供具体的功能;

next : 判断是上面的那种情况?

流程:
1.client 请求用于qq登录的网址(携带next参数,同下面的callback网址);
2.商城返回 qq登录网址 (没有向QQ服务器发送请求)
3.用户登录 qq 成功, QQ 通过302 重定向到 callback 网址 & 并授权code(这个code是在后面用于向QQ服务器请求access_token的) 和 state(同next,主要给前端使用)
访问 callback?code=xxx网址
4.凭借code向qq服务器请求access_token
5.QQ服务器返回access_token
6.商城服务器凭借access_token向qq服务器请求 openid(用户的唯一身份标识)
7.QQ服务器返回 openid
8. state 前端使用 ?????

QQ登录,相当于进行一次身份认证,和在商城进行登录两码事


数据库中表: 存放核心数据 +　扩展字段(补充字段,比如为了满足日后数据分析的需求建立的 create_time, update_time)
选项: 
auto_now_add 仅在新增的时候自动设置为当前时间;
update_now 操作修改时候 自动设置为当前时间;

需求: 扩展字段,不在数据库中创建表,'不真实存在' --> 在class Meata中设置类属性:abstract=True 抽象模型类,不在数据库中创建

一共在表中创建了多少个字段?
5个:　create_time , update_time id open_id user

如果是微信呢????

视图函数: 
1.获取查询参数  query_params.get('next')
2.封装一个通用的工具: 调用则拼接url , 使用了包 urllib.parse 的方法 urllib.parse.urlencode(字典)=>查询字符串
使用方式要参考 QQ 提供的 API 来固定的提供和拼接.
如果没有提供,则使用Django的默认配置,
setting -- django.conf 中 settings 
or 在给变量赋值 的高级 用法
3.抽象出来三个知识点:
3.1 面向对象的思想;
3.2 django的配置: django.conf.settings 而不是 buyfree_mall.settings.dev
3.3 urllib.parse包的使用(字典拼接成查询字符串)
    - 3.3.1 dict -> qs_str
    - 3.3.2 qs_str -> dict  => 一键多值
    - 3.3.3 获取url响应(data=''表示请求体,如果None就是get请求)体
    
-----------------------------
获取QQ用户openid接口
- 判断 是否有 openid? 如果没有,返回绑定接口; 如果有跳转到对应页面;
- 返回openid给前端,而且要防止前端修改, 使用 '成熟通用的解决方案' access_token, itsdangerous包=>用于生成各种jwt

序列化:
- 不仅限于django中使用,本质就是 数据格式转换器
- serializer.dumps;
- serializer.loads;
- serializer = Serializer(秘钥, 过期时间)

-----------------------------
通过code获取access_token
query_params.get('code')

封装方法,同上
拼接url,同上
from urllib.request import urlopen
resp = urlopen(url)
字节转化字符串 -> decode()
字符串->dict urllib.parse.parse_qs()  强调这里是查询字符串

链接网络 try... (自定义异常OAuthQQView, 主动抛出异常并被捕获, 同时记录到logger日志)
抛出异常原因,因为官方文档规定要返回 access_token,如果出现异常没法直接返回,所以才需要抛出???
在工具模块自定义异常,只需要继承 Exception 即可
在 调用 方法的的具体view中要 捕获异常

----------------------------
通过access_token获取 openid
查看API文档
获得结果后查询数据库,
也要捕获异常
根据查询结果进行不同的操作
如果出现异常(未查询到结果)
    - 使用itsdangerous模块: rest风格http无状态,不保存用户数据,所以就有了这个工具
    - 调用 封装 generate_bind_user_access_token(self,openid)
如果存在:
    - 签发token 并 返回 给前端,前端存储到 locationstorage 

前端在页面跳转callback的时候,会立即向后端回送一些数据来支持后端的查询
return 的字符串是在列表中

在之前的视图中添加 post 方法, 但是分析发现,可以继承 CreateAPIView ,就不用再写post
post方法中需要操作的是:
 -1. 获取数据()
 -2. 校验数据
 -3. 判断用户是否已经存在
    -3.1 如果存在, 绑定用户, 创建 OAuthQQUser 数据
    -3.2 如果不存在, 首先创建本地用户即生成User数据, 然后绑定QQ即创建OAuthQQUser
 -4. 签发jwt_token



这个和 get 不冲突
引入 序列化器(Modelserializer)

attrs 是跨字段的
validated_data 就是 跨字段校验过的 attrs




'''