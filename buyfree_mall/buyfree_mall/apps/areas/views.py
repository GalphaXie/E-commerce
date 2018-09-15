from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ReadOnlyModelViewSet

from areas.models import Area
from areas.serializers import AreaSerializer, SubAreaSerializer


class AreasViewSet(ReadOnlyModelViewSet):
    """
   行政区划信息
   # GET /areas/(?P<pk>\d+)/
   request: pk(int)
   response: id(int) name(str) subs(list)
   定义 查询集 和 序列化器的类 后面的源码方法就是 get_queryset 和 get_serializer_class ,这里根据需要直接重写方法

   """
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        """
        提供数据集
        """
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer
