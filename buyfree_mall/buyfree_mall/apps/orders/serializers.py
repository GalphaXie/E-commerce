from decimal import Decimal
import logging

from django.db import transaction
from django.utils import timezone
from django_redis import get_redis_connection
from rest_framework import serializers

from carts.serializers import CartSKUSerializer
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods

logger = logging.getLogger('django')


class OrderSettlementSerializer(serializers.Serializer):
    # max_digits 包含小数的最多位数，decimal_places 几位小数
    freight = serializers.DecimalField(max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True, read_only=True)


class SaveOrderSerializer(serializers.ModelSerializer):
    """
    下单数据序列化器
    """

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')  # order_id 不再是自增的主键,所以这里是双向的,要去设置为只读
        # 只读有两种设置方法
        read_only_fields = ('order_id',)
        extra_kwargs = {
            # 'order_id': {
            #     'read_only': True
            # },
            'address': {
                'write_only': True,
                'required': True
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }

        }

    #

    def create(self, validated_data):
        """保存订单"""
        address = validated_data['address']
        pay_method = validated_data['pay_method']

        # 获取用户对象 user
        user = self.context['request'].user

        # 查询购物车 sku_id count selected
        redis_conn = get_redis_connection('cart')

        # 获取 hash 数据
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        # 获取 set 数据
        redis_selected_cart = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        # 进行遍历
        for sku_id in redis_selected_cart:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        if not cart:
            raise serializers.ValidationError('没有需要结算的商品数据')

        # 创建事务,  开启事务
        with transaction.atomic():
            try:
                # 创建保存点
                save_id = transaction.savepoint()

                # 保存订单
                # 生成订单编号 2018010112:01:01000000001
                order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ("%09d" % user.id)
                # 1.创建订单基本信息表,OrderInfo
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'CASH'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                )

                # 查询数据库 获取商品数据(库存信息)
                sku_id_list = cart.keys()
                # sku_obj_list = SKU.objects.filter(id__in=sku_id_list)

                # 遍历需要结算的商品列表
                for sku_id in sku_id_list:
                    while True:
                        # 查询商品de 最新 库存信息
                        sku = SKU.objects.get(id=sku_id)
                        # 用户需要购买的数量
                        sku_count = cart[sku.id]
                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        # 判断库存(需要遍历操作,下面创建商品详情订单也需要遍历操作,所以 合并到一块儿在下面操作)
                        if origin_stock < sku_count:
                            # 回滚到保存点
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError('商品%s库存不足' % sku.name)

                        import time
                        time.sleep(5)

                        # # 库存减少,销量增加
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=SKU.id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        # 在Django 中 update 也会有返回值(返回受影响的行数)
                        if result == 0:
                            # 表示更新失败，有人抢了商品
                            # 结束本次while循环，进行下一次while循环
                            continue

                        order.total_count += sku_count
                        order.total_amount += (sku.price * sku_count)

                        # 2.创建订单商品信息表,OrderGoods
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price
                        )

                        # 跳出while循环，进行for循环
                        break

                order.save()
            except serializers.ValidationError:
                raise
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                raise
            else:
                transaction.savepoint_commit(save_id)

        # 删除购物车中已结算商品
        pl = redis_conn.pipeline()

        # hash
        pl.hdel('cart_%s' % user.id, *redis_selected_cart)

        # set
        pl.srem('cart_selected_%s' % user.id, *redis_selected_cart)

        pl.execute()

        # 返回 OrderInfo 对象
        return order
