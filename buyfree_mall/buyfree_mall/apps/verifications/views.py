from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.views import APIView
from buyfree_mall.libs.captcha.captcha import captcha

# 优雅的写法：自己的包导入和其他的都空一行，然后放在下面
from . import constants


class ImageCodeView(APIView):
    """
    图片验证码的处理视图
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
