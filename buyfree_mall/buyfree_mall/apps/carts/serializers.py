# -*- coding: utf-8 -*-
# @File : serializers.py
# @Author : Xie
# @Date   : 9/20/18
# @Desc   :
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """
    购物车数据序列化器
    """
    sku_id = serializers.IntegerField(label='sku id ', min_value=1)
    count = serializers.IntegerField(label='数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate(self, data):
        try:
            sku = SKU.objects.get(id=data['sku_id'])
        except SKU.DoesNotExist:
            raise ValidationError('商品不存在')

        # # 要和库存进行比较,这里要看产品需求设计
        # if data['count'] > sku.stock:
        #     raise serializers.ValidationError('商品库存不足')

        return data


class CartSKUSerializer(serializers.ModelSerializer):
    """购物车商品数据序列化器"""
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')


class CartDeleteSerializer(serializers.Serializer):
    """删除购物车数据序列化器"""
    sku_id = serializers.IntegerField(label='商品id', min_value=1)

    def validated_sku_id(self, value):
        try:
            sku = SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise ValidationError('商品不存在')
        return value
