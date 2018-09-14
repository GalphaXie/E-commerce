# -*- coding: utf-8 -*-
# @File : urls.py
# @Author : Xie
# @Date   : 9/11/18
# @Desc   :
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    # 登录认证 # obtain_jwt_token就是一个视图.as_view(),再通过前面的配置,然后来调用jwt_response_payload_handler方法
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^user/$', views.UserDetailView.as_view()),
    url(r'^emails/$', views.EmailView.as_view()),  # 设置邮箱
]
