import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

# POST /cart/
from carts import constants
from carts.serializers import CartSerializer


class CartView(APIView):  # 继承 GenericAPIView
    # cookies 请求,首先要修改后端的配置,允许在跨域请求中后端可以使用cookies;
    # 前端请求头中携带 Authorization, 可能为空; 防止后端异常,进行两个操作: 1. 重写验证前判断用户登录状态的方法; 2.捕获异常.

    def perform_authentication(self, request):
        """重写父类的用户验证方法,不在用户登录之前就验证jwt"""
        pass

    def post(self, request):
        """
        添加购物车
        # sku_id, count, selected
        如果用户登录: 保存到redis; 格式: hash->('user_id':{'sku_id':'count', 'sku_id':'count'}); set -> cart_selected_user_id : (sku_id, sku_id...)
        如果用户未登录: 保存到 cookies; 格式: cookies已经唯一标记一个用户了, 所以保存格式弄成json('字典'类型) {'sku_id':{'count':count, 'selected':selected}}
        - 需要进行格式的转换:　ｐｉｃｋｌｅ　－＞　ｂａｓｅ６４
        """
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 异常捕获: 尝试对请求的用户进行验证(上面的perform_authentication()重写,是为了让用户正常的进入视图方法中,但是这里还是要进行登录的验证)
        # 这里可以参看用户验证的时候源码, 返回的是 request.user 实际上这里和我们理解的不一样,这里user是属性方法
        try:
            user = request.user
        except:
            # 验证未通过
            user = None

        if user is not None and user.is_authenticated:  # 如果不进行这一步验证,前端可能通过请求头传递一个匿名用户对象: AnonymousUser
            # 用户已经登录,在redis中保存
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 记录购物车商品数量
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 记录购物车的勾选项
            # 勾选
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            # 用户未登录，在cookie中保存   response = Response()  response.set_cookie
            # {
            #     1001: { "count": 10, "selected": true},
            #     ...
            # }
            # 使用pickle序列化购物车数据，pickle操作的是bytes类型
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                # 解析
                cart_str = cart_str.encode()  # str-bytes  ???
                cart_bytes = base64.b64decode(cart_str)
                cart_dict = pickle.loads(cart_bytes)
            else:
                cart_dict = {}
            sku = cart_dict.get(sku_id, None)
            if sku:
                # 如果已经存在,那么累加商品,并且
                cart_dict[sku]['count'] += count
                cart_dict[sku]['selected'] = selected
            else:
                # 如果商品不在购物车中
                cart_dict[sku] = {
                    'count': count,
                    'selected': selected
                }
            cart_cookies = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 设置cookies
            response = Response(serializer.data)
            response.set_cookie('cart', cart_cookies, max_age=constants.CART_COOKIE_EXPIRES)
            return response

