from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 2  # 如果前端不传递值,默认每页显示的数据
    page_size_query_param = 'page_size'  # 指明有那个查询参数的值代表前端希望每页显示的数量
    max_page_size = 20  # 每页最大可以展示数据的数量
