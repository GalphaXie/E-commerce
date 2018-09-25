# -*- coding: utf-8 -*-
# @File : urls.py
# @Author : Xie
# @Date   : 9/11/18
# @Desc   :
from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from users import views

urlpatterns = [
    url(r'^users/$', views.UserView.as_view()),
    # 登录认证 # obtain_jwt_token就是一个视图.as_view(),再通过前面的配置,然后来调用jwt_response_payload_handler方法
    # url(r'^authorizations/$', obtain_jwt_token),  # 登录认证,
    url(r'^authorizations/$', views.UserAuthorizeView.as_view()),  # 登录认证, 补充了 合并购物车
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),  # 保证用户名的唯一性
    url(r'^user/$', views.UserDetailView.as_view()),  # 个人用户中心
    url(r'^email/$', views.EmailView.as_view()),  # 设置邮箱
    url(r'^browse_histories/$', views.UserBrowsingHistoryView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls

'''
router = routers.DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')
urlpatterns += router.urls
# POST /addresses/ 新建  -> create
# PUT /addresses/<pk>/ 修改  -> update
# GET /addresses/  查询  -> list
# DELETE /addresses/<pk>/  删除 -> destroy
# PUT /addresses/<pk>/status/ 设置默认 -> status
# PUT /addresses/<pk>/title/  设置标题 -> title
'''
