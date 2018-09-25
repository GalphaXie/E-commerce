import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, user, response):
    """
    合并cookie中的购物车数据到 reids
    :param request:
    :param user: 这里关键是: 为何要传递 user, 而不能通过 request.user 来提取呢???
    :param response:
    :return:
    """
    """
    登录时合并购物车，将cookie中的数据合并到redis中
    登录时，cookie中的数据如果存在与redis中相同的商品记录，如何处理的问题
    1. 商品数量： 以cookie为准
    2. 勾选状态： 以cookie为准

    合并前
    redis_cart = {
        '1': '20',
        '2': '2',
        '3': '5'
    }
    redis_cart_selected = set(1, 3)

    cookie_cart = {
        1: {
            'count': 10,
            'selected': False
        },
        4: {
            'count': 6,
            'selected': True
        }
    }
    合并后
    redis_cart = {
        '1': '10',
        '2': '2',
        '3': '5',
        '4': '6',
    }
    redis_cart_selected = set(3, 4)
    """
    # 获取cookie中的购物车数据
    cart_cookie = request.COOKIES.get('cart')
    if not cart_cookie:
        return response
    # 有购物车数据
    cart_dict = pickle.loads(base64.b64decode(cart_cookie.encode()))  # 解析

    # 获取redis中的购物车商品数量数据，hash
    redis_conn = get_redis_connection('cart')
    cart_redis = redis_conn.hgetall('cart_%s' % user.id)
    # cart_redis = {
    #     商品的sku_id  bytes字节类型: 数量  bytes字节类型
    #     商品的sku_id  bytes字节类型: 数量  bytes字节类型
    #    ...
    # }

    # 用来存储redis最终保存的商品数量信息的hash数据
    cart = {}
    for sku_id, count in cart_redis.items():
        cart[int(sku_id)] = int(count)

    # 用来记录redis最终操作时，哪些sku_id是需要勾选新增的
    cart_redis_selected_add = []

    # 用来记录redis最终操作时，哪些sku_id是需要取消勾选删除的
    cart_redis_selected_remove = []

    # 遍历cookie中的购物车
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
    for sku_id, count_selected_dict in cart_dict.items():
        #  处理商品的数量，维护在redis中购物车数据数量的最终字典
        cart[sku_id] = count_selected_dict['count']

        # 处理商品的勾选状态
        if count_selected_dict['selected']:
            # 如果cookie指明，勾选
            cart_redis_selected_add.append(sku_id)
            # 如果cookie指明，不勾选
            cart_redis_selected_remove.append(sku_id)
    if cart:
        # 执行redis操作
        pl = redis_conn.pipeline()

        # 设置hash类型
        pl.hmset('cart_%s' % user.id, cart)

        # 设置set类型
        if cart_redis_selected_remove:
            pl.srem('cart_selected_%s' % user.id, *cart_redis_selected_remove)
        if cart_redis_selected_add:
            pl.sadd('cart_selected_%s' % user.id, *cart_redis_selected_add)

        pl.execute()

    # 删除cookie
    response.delete_cookie('cart')
    return response
