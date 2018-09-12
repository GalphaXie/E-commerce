# -*- coding: utf-8 -*-
# @File : utils.py
# @Author : Xie
# @Date   : 9/12/18
# @Desc   :
import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """

    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 账号为手机号
            user = User.objects.get(mobile=account)
        else:
            # 账号为用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 获取用户对象
        user = get_user_by_account(username)
        # 如果用户对象存在,那么校验密码,如果密码校验通过,那么返回用户
        if user is not None and user.check_password(password):  # 用户传递过来的密码是需要django自带的方法来校验的
            return user
