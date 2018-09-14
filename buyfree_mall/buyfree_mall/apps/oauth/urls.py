# -*- coding: utf-8 -*-
# @File : urls.py
# @Author : Xie
# @Date   : 9/12/18
# @Desc   :
from django.conf.urls import url

from oauth import views

urlpatterns = [
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    url(r'^qq/user/$', views.OAuthQQUserView.as_view()),
]
