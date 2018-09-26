from django.test import TestCase

# Create your tests here.

"""
表单设计--关键点:
- 1.用特殊的订单编号(指明primary_key) 来代替 自增主键
- 2. decimal 来 控制精度 
- 3. choice 枚举

回滚 注意点:
- 数据库出现异常才会回滚






"""