# -*- coding: utf-8 -*-
# @File : utils.py
# @Author : Xie
# @Date   : 9/12/18
# @Desc   :
import urllib.parse

from django.conf import settings


class OAuthQQ():

    def __init__(self, client_id=None, redirect_uri=None, state=None):
        self.client_id = client_id if client_id else settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri if redirect_uri else settings.QQ_REDIRECT_URI
        # self.state = state if state else settings.QQ_STATE
        # 法二:
        self.state = state or settings.QQ_STATE

    def get_login_url(self):
        url = 'https://graph.qq.com/oauth2.0/authorize?'
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
        }

        url += urllib.parse.urlencode(params)

        return url
