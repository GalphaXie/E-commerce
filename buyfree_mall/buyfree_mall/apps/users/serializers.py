# -*- coding: utf-8 -*-
# @File : serializers.py
# @Author : Xie
# @Date   : 9/11/18
# @Desc   :
import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    '''使用模型序列化器的两个功能:　1.校验; 2.保存数据'''

    # 下面三个是模型类中没有的,需要自己再补充;同时,序列化器可以双向处理数据,必须对字段进行指明来取代默认的都是双向处理.
    password2 = serializers.CharField(label='确认密码', write_only=True)
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    allow = serializers.BooleanField(label='同意协议', write_only=True)

    # 添加字段
    token = serializers.CharField(label='jwt token', read_only=True)

    class Meta:
        model = User
        # fields 中拿取的不止 model属性指明的模型类中的字段,还包括我们 需要主动添加的 字段
        # 关于id字段的说明: id是数据库自增生成的,drf默认不需要前端传递过来; 这里没有'限制'其返回,所以可以不用设置只需要添加在fields中就可以返回.
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow', 'token')

        # 通过 extra_kwargs 来配置字段额外的申明
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    # 防止缩进错误
    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式错误')
        return value

    def validate_allow(self, value):
        """检验用户是否同意协议"""
        if value != True:
            raise serializers.ValidationError('请同意用户协议')
        return value

    def validate(self, data):
        # 判断两次密码
        if data['password'] != data['password2']:
            raise serializers.ValidationError('两次密码不一致')

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code is None:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    # 模型序列化器保存, User中有一个特殊的: password,必须要先加密再保存
    def create(self, validated_data):
        '''重写保存方法,增加密码加密'''

        # 移除数据库模型类中不存在的属性
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 方式一: 原始的数据库的方式
        # user = User.objects.create(**validated_data)
        # 方式二: Modelserializers 的方法 (不需要拆包)
        user = super().create(validated_data)

        # 调用django的认证系统加密密码
        user.set_password(validated_data['password'])

        user.save()

        # 签发 jwt token ; 注意:导入 从rest_framework_jwt
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user.token = token

        # return 最终会被序列化的数据,可以是  模型对象 或 validated_data
        return user
