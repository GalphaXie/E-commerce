from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from order.serializers import OrderSettlementSerializer


class OrderSettlementView(APIView):  # 不继承List...,因为是对应列表类型,这里是大字典的数据设计
    """
    订单结算
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取"""
        # 获取用户对象
        user = request.user

        # 查询redis
        redis_conn = get_redis_connection('cart')

        # 获取 hash 数据
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        # 获取 set 数据
        redis_selected_cart = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        # 进行遍历
        for sku_id in redis_selected_cart:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息(mysql数据库)
        sku_id_list = cart.keys()
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)

        # 给商品添加属性
        for sku in sku_obj_list:
            sku.count = cart[sku.id]
            sku.selected = True

        # 运费
        freight = Decimal('10.00')

        # 序列化返回
        # serializer = CartSKUSerializer(sku_obj_list, many=True)
        # return Response({'freight': freight, 'skus': serializer.data})

        serializer = OrderSettlementSerializer({'freight': freight, 'skus':sku_obj_list}, many=True)
        return Response(serializer.data)


