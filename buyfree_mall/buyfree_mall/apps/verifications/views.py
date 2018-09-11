import random

from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from buyfree_mall.libs.captcha.captcha import captcha
import logging

# 优雅的写法：自己的包导入和其他的都空一行，然后放在下面
from buyfree_mall.utils.yuntongxun.sms import CCP
from verifications.serializers import ImageCodeCheckSerializer
from . import constants

logger = logging.getLogger('django')


# url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
class ImageCodeView(APIView):
    """
    图片验证码的处理视图
    重要逻辑:为何不需要使用序列化器？　为何选择继承APIView类而不是其他？
    """

    def get(self, request, image_code_id):
        """
        获取图片验证码
        """
        # 生成验证码图片
        text, image = captcha.generate_captcha()
        # django-redis提供了get_redis_connection的方法，通过调用get_redis_connection方法传递redis的配置名称
        # 可获取到redis的连接对象，通过redis连接对象可以执行redis命令
        redis_conn = get_redis_connection("verify_codes")  # 获取跟验证码相关系的链接
        # 保存的是str， setex(k， 过期时间， v)
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 固定返回验证码图片数据，不需要REST framework框架的Response帮助我们决定返回响应数据的格式
        # 所以此处直接使用Django原生的HttpResponse即可
        return HttpResponse(image, content_type="images/jpg")


# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """
    短信验证码
    传入参数：
        mobile, image_code_id, text
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):  # 两个查询字符串参数不需要 写形式参数
        # 校验参数 由序列化器完成? 为什么 : 除了url路径中的mobile参数外,image_code_id, text都是查询参数,不受url匹配控制所以要校验
        serializer = self.get_serializer(data=request.query_params)  # 必须指明data=
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码,
        sms_code = '%06d' % random.randint(0, 999999)

        # 并记录 内容 和 请求验证码的频率
        redis_conn = get_redis_connection('verify_codes')
        # redis 管道
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 让管道通知redis执行命令
        pl.execute()

        # 发送短信验证码
        try:
            sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)  # 地板除
            ccp = CCP()
            result = ccp.send_template_sms(mobile, [sms_code, sms_code_expires],
                                           constants.SMS_CODE_TEMP_ID)  # 注意： 测试的短信模板编号为1
        except Exception as e:
            logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
            return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if result == 0:
                logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
                return Response({'message': 'OK'})
            else:
                logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
                return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 响应 (不是从数据库返回的数据,简单的数据,不需要序列化器)
