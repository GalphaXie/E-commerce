# -*- coding: utf-8 -*-
# @File : models.py
# @Author : Xie
# @Date   : 9/12/18
# @Desc   :
from django.db import models


# 对于以后的数据分析需求,很多字段都会要求来判断用户的创建时间和修改时间,这个类就是创建来给别人继承用的.
class BaseModel(models.Model):
    """为模型类补充字段"""
    create_time = models.DateField(auto_now_add=True, verbose_name='创建时间')  # auto_now_add 表示在第一次创建的时候记录
    update_time = models.DateField(auto_now=True, verbose_name='更新时间')  # auto_now 表示每次修改就会记录

    class Meta:
        abstract = True  # 说明是抽象模型类,用于继承使用,数据库迁移时不会创建BaseModel的表
