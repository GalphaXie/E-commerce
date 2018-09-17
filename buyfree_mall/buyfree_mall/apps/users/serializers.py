# -*- coding: utf-8 -*-
# @File : serializers.py
# @Author : Xie
# @Date   : 9/11/18
# @Desc   :
import re

from django_redis import get_redis_connection
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from celery_tasks.email.tasks import send_verify_email
from users.models import User, Address


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
    # 对validate_字段名 对单个字段进行 '自己代码' 的校验
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

    # 密码 整体校验
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


class UserDetailSerializer(serializers.ModelSerializer):
    '''
    username, mobile, email id email_active
    该序列化器不需要进行校验操作,只需要向前端返回
    '''

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'email_active')  # id 自增的,不需要前端传递


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email')
        # 这里邮箱都不需要自己校验,因为邮箱格式都是一样,而且自带了校验;因为AbstractUser有字段email,对应到序列化器Serializer.EmailField()
        extra_kwargs = {
            'email': {
                'required': True
            }
        }

    def update(self, instance, validated_data):
        '''

        :param instance: 视图传递过来的user对象
        :param validated_data:
        :return:
        '''
        email = validated_data['email']
        url = instance.generate_verify_email_url()
        send_verify_email.delay(email, url)
        return instance


class UserAddressSerializer(serializers.ModelSerializer):
    """
    用户地址序列化器
    tb_address表中对应的字段:　
    id create_time update_time title receiver place mobile tel email is_delete city_id district_id province_id user_id
    """
    # 可以发现　模型类　中　外键字段　是以　id 存储的, 但是可以取出其 对应的 对象, 所以在序列化器中可以直接写 id 对应的 对象名字 等字段
    # 前端传递回来的是 id ; 而我们要给前端展示的是 对象name
    # 下面只对 三个 外键 标记的字段作了 选项的操作
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def validate_mobile(self, value):
        """校验手机号"""
        if not re.match(r'1[3-9]\d{9}$', value):
            return serializers.ValidationError('手机格式错误')
        return value

    def create(self, validated_data):
        """保存数据"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AddressTitleSerializer(serializers.ModelSerializer):
    """
    地址标题
    """
    class Meta:
        model = Address
        fields = ('title',)  # 元组字段
