from django.shortcuts import render

# Create your views here.
from rest_framework.filters import OrderingFilter

from rest_framework.generics import ListAPIView

from buyfree_mall.utils.pagination import StandardResultsSetPagination
from goods.filters import CateFilter
from goods.models import SKU
from goods.serializers import SKUSerializer


# rest 风格推荐，　以查询字符串的形式获取　列表　的(过滤)信息
# /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    """
        sku 列表　数据  (要分别实现:　分页，　排序，　过滤)
        分页： 这次采取前端可以适当传值 page_size 来确定 每页接收多少数据
        同时: drf 还自动提供了特殊的 几个 字段来帮助我们实现 功能 总页count, pre, next, results(包含商品的所有信息)
     """
    serializer_class = SKUSerializer
    # queryset = SKU.objects.filter(category_id=...?) 取不到 request.query_id

    # 排序
    filter_backends = [OrderingFilter, ]  # drf 中提供了 排序(当做一种特殊的过滤处理)
    ordering_fields = ('create_time', 'price', 'sales')

    # 分页
    # 法一:在全局配置

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)  # 外键.有两个属性 category 和 category_id


'''
# 实现思路二：
# /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    """
        sku 列表　数据  (要分别实现:　分页，　排序，　过滤)
        分页： 这次采取前端可以适当传值 page_size 来确定 每页接收多少数据
        同时: drf 还自动提供了特殊的 几个 字段来帮助我们实现 功能 总页count, pre, next, results(包含商品的所有信息)
     """
    serializer_class = SKUSerializer
    queryset = SKU.objects.filter(is_launched=True)

    # 排序
    filter_backends = [OrderingFilter, CateFilter]  # drf 中提供了 排序(当做一种特殊的过滤处理)
    ordering_fields = ('create_time', 'price', 'sales')
    pagination_class = StandardResultsSetPagination

    # 分页  个性化配置
'''
