# -*- coding: utf-8 -*-
# @File : urls.py
# @Author : Xie
# @Date   : 9/15/18
# @Desc   :
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas import views

router = DefaultRouter()

router.register('areas', views.AreasViewSet, base_name='areas')

urlpatterns = []

urlpatterns += router.urls
