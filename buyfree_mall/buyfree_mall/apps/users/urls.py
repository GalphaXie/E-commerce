# -*- coding: utf-8 -*-
# @File : urls.py
# @Author : Xie
# @Date   : 9/11/18
# @Desc   :
from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view())
]
