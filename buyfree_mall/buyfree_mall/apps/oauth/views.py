from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from oauth.exceptions import OAuthQQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    '''
    获取QQ登录的url  ?next=xxx
    '''

    def get(self, request):
        # 获取next参数
        next = request.query_params.get('next')

        # 拼接QQ登录的网址
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_login_url()
        # print(login_url)

        # 返回
        return Response({'login_url': login_url})


# url(r'/qq/user/$', views.QQAuthUserView.as_view()),
# class QQAuthUserView(APIView):
class OAuthQQUserView(CreateAPIView):
    """
    QQ 登录的用户, ?code=xxx
    """
    # 实现 绑定QQ用户的操作
    serializer_class = OAuthQQUserSerializer

    # 要使用post方法来提交表单,然后进行序列化器校验,返回结果;发现通用的写法CreateAPIView已经实现
    # 所以将上面的类重新继承 CreateAPIView
    # def post(self, request):
    # pass

    # 继续查看 API 接口文档
    def get(self, request):
        # 获取code
        code = request.query_params.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        # 通过工具获取access_token
        oauth_qq = OAuthQQ()
        try:
            # 凭借code 获取access_token
            access_token = oauth_qq.get_access_token(code)

            # 凭借access_token获取 openid
            openid = oauth_qq.get_openid(access_token)

        except OAuthQQAPIError:
            return Response({'message': '访问QQ接口异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 根据openid查询数据库OAuthQQUser  判断数据是否存在
        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在，处理openid  要求用户绑定并注册 , 返回
            access_token = OAuthQQ.generate_bind_user_access_token(openid)
            return Response({'access_token': access_token})
        else:
            # 如果数据存在，表示用户已经绑定过身份， 签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            # 签发的时候,要向 jwt_payload_handler 传递 user对象
            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

        # return Response({
        #     'token': token,
        #     'username': user.username,
        #     'user_id': user.id
        # })
        response = Response({
            'token': token,
            'username': user.username,
            'user_id': user.id
        })

        # 合并购物车
        merge_cart_cookie_to_redis(request, user, response)

        return response

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # 合并购物车
        user = self.user
        merge_cart_cookie_to_redis(request, user, response)

        return response






