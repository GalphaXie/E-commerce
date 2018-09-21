# -*- coding: utf-8 -*-
# @File : urls.py
# @Author : Xie
# @Date   : 9/20/18
# @Desc   :
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from goods import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/skus/$', views.SKUListView.as_view()),
]

router = DefaultRouter()  # 这里导包不要导包成 haysatack...

router.register('skus/search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls
