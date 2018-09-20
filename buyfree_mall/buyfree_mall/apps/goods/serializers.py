# -*- coding: utf-8 -*-
# @File : serializers.py
# @Author : Xie
# @Date   : 9/19/18
# @Desc   :
from rest_framework import serializers

from goods.models import SKU


# 在users 的 app 中 serializers.py 文件有定这个,这里自己再定义一下,用于独立和区分
class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')
