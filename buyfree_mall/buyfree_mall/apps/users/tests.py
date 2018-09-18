from django.test import TestCase

# Create your tests here.

'''
pycharm 快捷键  ctrl shift - | ctrl shift + 快速折叠或者展开类(函数)  阅读源码有奇效

--------------------------------------------------
实现功能:
1.email & 激活状态 -> user模型自带email,但是激活状态不能用is_active,所以添加字段,数据库迁移

2.GET ; url路径: /users/<user_id>/  -> 但是标记的是token而不是id, 所以 /user/ 复数变单数

3. request:  username mobile email email_active

4. response : id username mobile email email_active

难点:视图的理解:
查寻数据 -> 序列化数据 => retrieve -> RetrieveAPIView(RetrieveModelMixin, GenericAPIView)

(继承的时候,子类不存在的方法需要调用父类的,如果父类中在该方法中又调用了另外一个方法,而这个方法在父类和子类中都有,那么会优先调用子类的,从而达到重写的目的.这种只是更加复杂一点重写而已.)

序列化器: 
class

访问view视图详情的时候, 为什么要重写 get_object方法? 返回当前的用户对象?
queryset (retrieve 对其进行过滤,才会只有一个结果返回) 其默认依赖实现是: /users/<pk>/ 这两者都没有实现  => 重写 get_object

返回数据,获得验证过的当前的用户,而这个在当前请求的 user 属性. request.user (不能直接拿到)
要在 类视图对象中,可以通过类视图对象获取属性request. (视频中老师源码看错误,应该看 APIView的dispatch方法的 self.request= request)

serializer_class = ?

为何要增加认证?
必须登录认证之后才能访问 get_object 方法

前端实现: jwt 规范的做法:请求头中实现
记住登录: localStorage ; 否则是 SessionStorage
token:　没有权限　status:403；或　过期
str.split() -> 列表，默认是以空格分割　JWT空格str

获取token值来判断用户身份的方式:
1.前端传递了token值; 2.我们在在配置中配置了 DEFAULT_AUTHENTICATION_CLASSES

----------------------------------------------------
PUT /users/<user_id>/email -> email

发送邮件的前置准备工作

SMTP 是发送邮件的服务器   vs    IMAP POP3 是收邮件的服务器(其中IMAP支持交互操作,双向保存等,POP3只支持下载保存)
port 25
授权码

Django 发送邮件 : 1.配置(现成的模块);2.发送(django.core.mail 的 send_mail方法)



celery 发送操作
celery依赖django的配置,不要忽略
send_mail(subject, message, from_email, recipient_list,html_message=None) 参数:

链接: (token) 需要进行处理,防止用户激活的时候修改 激活链接

给 django自带的User模型类中仿照自带的一些方法,添加一个自定义的方法

自定义方法是添加token的方法,没太懂?
generate_verify_email_url 和 check_verify_email_token 这种对称的套路方法,都是是用 itsdangerous 包 TJWSSerializer 
dumps. decode  ;  loads 

序列化器的update方法中, save()的位置? 因为下面调用自定义方法的时候需要使用email,所以要先save

激活:
post or get 理解:
get没有请求体, delete可以有可以没有... 这里把token放在url?后面

--------------------------------------------------------
新版的django 的 ForeignKey(必须设置 on_delete 选项)  选项: related_name 类似flask的backref
自关联要点：
－　外键　 'self' ; 这里其实可以写字符串或者类名(如果不是在同一py文件,那么要把app名加上:app名.类名)；　但是＇解释性＇语言，所以可能会出错；通用的方法是； 都写字符串
- relate_name 多个外键,就可能存在问题

数据库迁移：　
apps 新建的必须要注册到 dev的配置文件中,否则是没法进行数据库迁移的.
导入数据库文件方式--测试脚本实现:
1.  < 
2.  # !
命令:mysql -h数据库ip地址 -u数据库用户名 -p 数据库名 < areas.sql  老师的课件是错误的
mysql -h127.0.0.1 --port=3306 -ubuyfree -p buyfree_mall < areas.sql  (mysql数据库端口命令可以省略)
修改文件的执行权限 chmod +x import_areas_data_to_db.sh
执行命令导入数据:　./import_areas_data_to_db.sh



-------------------------------------------------------
实现省市区的接口:
所在地区:两个接口, 省是一打开就加载; 后面的市区可以共用一个接口
subs 属性,多

视图集: 视图方法的集合
视图集用: router方法来注册.    DefaultRouter类() -> router  -> router.register(prefix, viewset, verbose_name) -> urlpatterns += router.urls



缓存:

关闭分页处理:　None


继承的顺序, Mixin 都写到前面 (强制记住) 

------------------------------------------------------------
用户地址管理
分析: 用户地址数量不定(<=20)  -> 不能放在 user 模型一起 -> 新建一个表

默认地址 -> 两种方法:　第一种-在address表中标记为default_address=True,修改麻烦,且容易造成一个用户有多个默认地址;  采取第二种－用户表中增加一个字段指向address
可以在 class Meta中设置 ordering = ['-update_time']  来指明 每次查询的默认排序方式

关于视图集使用-- 解决现实问题:  地址栏有6个接口,分别用了各种methods,且他们的url资源都是关于 /addresses/ 的
get  查询  /addresses/  (/addresses/<pk>/ 不查询)
post 增加  /addresses/  (糊涂,增加这里哪有 <pk>, 这个id是数据库自动生成的,是不是傻 但是这里为何用复数呢?)
put  修改  /addresses/<pk>/
delete 删除  /addresses/<pk>/
put  设置默认地址  /addresses/<pk>/status/   (/users/<user_id>/addresses/<pk>/status/ 改成django风格,用户登录之后才会能修改,所以把前面去掉,为了统一到一个视图集中该操作)
put  设置地址的标题 /addresses/<pk>/title/
#　url资源统一之后 符合 rest 风格, 才能更好的调用 视图集; 这个可以通过前面又一次不符合规范而没用的那个视图来验证

***********************************************
# 这里面导入的是 GenericViewSet, 而不是 GenericAPIView
这里如何理解? 并不容易
为何要继承 UpdateModelMixin  ? 只是使用了它的校验?  它们映射 了 methods -> action

到底如何选择个性化字段?
映射到 对应的模型类 还要结合数据库表的字段


python manage.py shell  如何使用? 导包出现问题...


***********************************************

补充重要知识点:
　关于外键字段：　一个外键字段，Django自动让其包含两个值:  模型类名.字段名 => 字段对象;  模型名.字段名_id => 字段对象的id(django 自动补充的);  这个两个结果在 查询和创建 的时候都会产生  





'''
