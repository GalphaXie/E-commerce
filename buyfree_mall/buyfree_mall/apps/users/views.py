from django.shortcuts import render

# Create your views here.


# url(r'^users/$', views.UserView.as_view()),
from rest_framework.generics import CreateAPIView

from . import serializers


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = serializers.CreateUserSerializer
