# -*- coding: utf-8 -*-
# @File : utils.py
# @Author : Xie
# @Date   : 9/12/18
# @Desc   :
import urllib.parse
import urllib.request
import logging
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings

from oauth import constants
from oauth.exceptions import OAuthQQAPIError

logger = logging.getLogger('django')


class OAuthQQ(object):

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id if client_id else settings.QQ_CLIENT_ID
        self.redirect_uri = redirect_uri if redirect_uri else settings.QQ_REDIRECT_URI
        # self.state = state if state else settings.QQ_STATE
        # 法二:
        self.state = state or settings.QQ_STATE
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET

    # 这里是参照 QQ 提供的 API 接口: http://wiki.connect.qq.com/%E4%BD%BF%E7%94%A8authorization_code%E8%8E%B7%E5%8F%96access_to
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

    # 再次查看 API 文档
    def get_access_token(self, code):
        '''
        access_token 授权令牌; expires_in 有效期; refresh_token
        :param code:
        :return:
        '''
        url = 'https://graph.qq.com/oauth2.0/token?'
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        url += urllib.parse.urlencode(params)

        try:
            resp = urllib.request.urlopen(url)  # 发送请求,返回HTTPResponse对象
            resp_data = resp.read()  # read读取,结果是bytes
            resp_data = resp_data.decode()  # 转码 查询str
            # 'access_token=FE04************************CCE2 & expiresin=7776000 & refreshtoken=88E4***********BE14'
            # access_token 只是字符串中的一部分,所以要转化成dict才可以取出 #解析 access_token
            resp_dict = urllib.parse.parse_qs(resp_data)  # dict
            access_token = resp_dict.get('access_token')
        except Exception as e:
            logger.error('获取access_token异常：%s' % e)
            raise OAuthQQAPIError
        else:
            return access_token[0]

    def get_openid(self, access_token):
        """通过 access_token 来获取 openid"""
        url = 'https://graph.qq.com/oauth2.0/me'
        params = {
            'access_token': access_token
        }
        url += urllib.parse.urlencode(params)
        try:
            resp_data = urllib.request.urlopen(url).read().decode()  # 查询str
            # 其返回字符串如下:
            # callback( {"client_id": "YOUR_APPID", "openid": "YOUR_OPENID"} )\n;
            resp_data = resp_data[10:-4]
            resp_dict = urllib.parse.parse_qs(resp_data)
            open_id = resp_dict.get('openid')
        except Exception as e:
            logger.error('获取openid异常：%s' % e)
            raise OAuthQQAPIError
        else:
            return open_id

    @staticmethod
    def generate_bind_user_access_token(openid):
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({'openid': openid})
        return token.decode()

    @staticmethod
    def check_bind_user_access_token(access_token):
        serializer = TJWSSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data['openid']
