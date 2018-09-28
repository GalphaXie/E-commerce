import base64
import pickle

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

# POST /cart/
from rest_framework.views import APIView

from carts import constants
from carts.serializers import CartSerializer, CartSKUSerializer, CartDeleteSerializer, CartSelectAllSerializer
from goods.models import SKU


class CartView(GenericAPIView):  # 继承 GenericAPIView
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
        except Exception:
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
                cart_dict[sku_id]['count'] += count
                cart_dict[sku_id]['selected'] = selected
            else:
                # 如果商品不在购物车中
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            cart_cookies = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 设置cookies
            response = Response(serializer.data)
            response.set_cookie('cart', cart_cookies, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def get(self, request):
        """查询购物车"""
        # 1. 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        # 查询
        if user and user.is_authenticated:
            # 2. 如果已登录,那么从redis 中查询  :  sku_id, count, selected
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall("cart_%s" % user.id)  # redis 中虽然保存的都是字典,但是具体的数据类型都是bytes
            # redis_cart = {
            #     商品的sku_id  bytes字节类型: 数量  bytes字节类型
            #     商品的sku_id  bytes字节类型: 数量  bytes字节类型
            #    ...
            # }
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            # redis_cart_selected = set(勾选的商品sku_id bytes字节类型, ....)

            # 遍历 redis_dict , 形成 cart_dict
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),  # 可以直接将bytes转成python中的int
                    'selected': sku_id in redis_cart_selected  # in 直接来形成 True|False
                }
        else:
            # 3. 如果未登录, 那么从 cookies 中查询: ...
            cookie_cart = request.COOKIES.get('cart', None)  # 前面设置的cookies中的名字就是 cart
            if cookie_cart:
                # 表示cookie中有购物车数据
                # 解析
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

        # 不论是否登录,最终都处理成 下面的 数据结构设计
        # cart_dict = {
        #     sku_id_1: {
        #         'count': 10
        #         'selected': True
        #     },
        #     sku_id_2: {
        #         'count': 10
        #         'selected': False
        #     },
        # }

        # 4. 查询数据库,获取商品的详细信息
        sku_id_list = cart_dict.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)

        # 遍历sku_obj_list 向sku对象中添加count和selected属性
        for sku in sku_obj_list:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 5. 序列化返回
        serializer = CartSKUSerializer(sku_obj_list, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车数据"""
        # sku_id, count, selected
        # 校验
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        count = serializer.validated_data['count']
        selected = serializer.validated_data['selected']

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None
        if user and user.is_authenticated:
            # 已登录,查询 修改 redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 处理count
            pl.hset('cart_%s' % user.id, sku_id, count)
            # 处理 selected 状态
            if selected:
                # 表示勾选
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            else:
                # 取消勾选
                pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            # 序列化返回
            return Response(serializer.data)

        else:
            # 未登录,查询 修改 cookie
            cart_cookie = request.COOKIES.get('cart')
            if cart_cookie:
                # 表示cookie中有购物车数据
                # 解析
                cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                # 表示 cookie 中没有购物车数据
                cart_dict = {}

            response = Response(serializer.data)

            # 修改 cookie 中的cart数据
            if sku_id in cart_dict:
                # 存在购物车数据, 进行修改
                cart_dict['sku_id'] = {
                    'count': count,
                    'selected': selected
                }
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()

                # 序列化返回
                # 设置cookie
                response.set_cookie('cart', cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)
            return response

    def delete(self, request):
        """删除购物车数据"""
        # 校验参数(sku_id是否符合规范, 商品是否存在)
        serializer = CartDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data['sku_id']
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            # 登录, 删除 redis
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
            # 删除 hash
            pl.hdel('cart_%s' % user.id, sku_id)
            # 删除 set
            pl.srem('cart_selected_%s' % user.id, sku_id)
            pl.execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 未登录, 删除 cookie
            cart_cookie = request.COOKIES.get('cart')
            response = Response(status=status.HTTP_204_NO_CONTENT)
            if cart_cookie:
                # cookie中有购物车数据
                # 解析
                cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))
            else:
                # 没有购物车数据
                cart_dict = {}
            if sku_id in cart_dict:
                # 删除
                del cart_dict[sku_id]

                # 数据序列化操作
                cart_cookie = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                response.set_cookie('cart', cart_cookie, max_age=constants.CART_COOKIE_EXPIRES)
            return response


class CartSelectAllView(APIView):
    """购物车全选"""

    def perform_authentication(self, request):
        pass

    def put(self, request):
        serializer = CartSelectAllSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        selected = serializer.validated_data['selected']

        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user and user.is_authenticated:
            # 用户已登录, 操作 redis
            redis_conn = get_redis_connection('cart')
            sku_id_list = redis_conn.hgetall('cart_%s' % user.id)

            if selected:
                # 将购物车中所有的商品sku_id全部加入 set
                redis_conn.sadd('cart_selected_%s' % user.id, *sku_id_list)
            else:
                # 反选, 执行删除操作
                redis_conn.srem('cart_selected_%s' % user.id, *sku_id_list)
            return Response({'message': 'OK'})
        else:
            # 用户未登录,操作 cookie
            cart_cookies = request.COOKIES.get('cart')
            if cart_cookies:
                # cookie 中有 购物车 数据
                cart_dict = pickle.loads(base64.b16decode(cart_cookies.encode()))
            else:
                cart_dict = {}

            # cart_dict = {
            #     sku_id_1: {
            #         'count': 10
            #         'selected': True
            #     },
            #     sku_id_2: {
            #         'count': 10
            #         'selected': False
            #     },
            # }

            response = Response({'message': 'OK'})

            for count_selected_dict in cart_dict.values():
                count_selected_dict['selected'] = selected

            # 设置 cookies 并 返回
            cart_cookies = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response.set_cookie('cart', cart_cookies, max_age=constants.CART_COOKIE_EXPIRES)
            return response
