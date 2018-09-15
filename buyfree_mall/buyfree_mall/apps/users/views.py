from django.shortcuts import render

# Create your views here.


# url(r'^users/$', views.UserView.as_view()),
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from . import serializers


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = serializers.CreateUserSerializer


# 分析: 接受前端通过正则校验过的数据,到数据库查询用户名的数量,返回给前端
# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """

    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """

    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


# GET /user/  根据rest风格,本来要是 /users/<user_id>/  ,但是能进入个人中心,用户身份已经确定,采取了改复数为单数
class UserDetailView(RetrieveAPIView):
    '''用户的基本信息'''

    serializer_class = serializers.UserDetailSerializer
    # queryset = User.objects.all()

    permission_classes = [IsAuthenticated]  # 指明必须登录认证后才能访问

    def get_object(self):
        # 返回当前请求的用户
        # 在类视图对象中，可以通过类视图对象的属性获取request
        # 在django的请求request对象中，user属性表明当请请求的用户
        return self.request.user


# 　put /email/  <-  rest /users/<user_id>/email
class EmailView(UpdateAPIView):
    '''
    保存邮箱
    '''
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """
    邮箱验证
    这里可以采用 get 或 post 多种请求方式,但是这里采取 get 请求
    request参数:　token=?
    response参数: message
    """

    def get(self, request):
        # 接收参数
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        # 校验参数 token
        user = User.check_verify_email_token(token)  # 校验token是属于 User模型的一个字段, 再借鉴User的封装的方法,我们可以自己定义模型类的方法

        if not user:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 如果token正常传递过来,那么激活成功,在数据库中进行标记 email_active
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})  # 返回成功
