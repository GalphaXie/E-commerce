from django.test import TestCase

# Create your tests here.

"""
商品和广告,可能是由两个团队分别维护的,所以这里创建两个app应用: contents(广告内容) 和 goods(商品)
APP 创建完成后,首先要注册到 APP_INSTALL, 然后创建模型类之后才能顺利的进行数据库迁移
先有的数据表设计和表间关系, 后面才有 模型类












"""