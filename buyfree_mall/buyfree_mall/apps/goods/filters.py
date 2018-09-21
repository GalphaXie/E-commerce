# -*- coding: utf-8 -*-
# @File : filters.py
# @Author : Xie
# @Date   : 9/20/18
# @Desc   :
from django.db.models import QuerySet
from rest_framework.filters import BaseFilterBackend


class CateFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset: QuerySet, view):  # 添加一个提示QuerySet
        queryset = queryset.filter(category_id=view.kwargs['category_id'])
        return queryset
