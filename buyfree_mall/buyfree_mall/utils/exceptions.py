from rest_framework.views import exception_handler as drf_exception_handler
import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status

# 获取在配置文件中定义的logger，用来记录日志
logger = logging.getLogger('django')


def exception_handler(exc, context):
    """
    自定义异常处理
    :param exc: 异常
    :param context: 抛出异常的上下文
    :return: Response响应对象
    """
    # return None
    # 调用drf框架原生的异常处理方法
    response = drf_exception_handler(exc, context)  # rest提供的方法如果不能处理的异常，该函数最后会返回 None。

    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 数据库异常
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response


# 异常处理的思路:
# 1.1异常分类成 个性化异常
# 1.2异常分类成 可以集中处理的异常；
# 2 这里自定义的异常就是来处理 mysql和redis的异常，我们来借鉴 rest_framework 自带的异常处理机制
# 3.自己封装的 代表性的工具，所以选择放在 utils ，而不是 外面的 __init__。
# 4.导包的时候为了不覆盖，所以这里就用了 as，这是一个技巧，类似‘装饰器’思想，在同级中添加功能。
