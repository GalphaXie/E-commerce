# 这里操作的都是 haystack 的语法
# 类似drf 的 模型类(操作ORM,数据库)
from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # 作用: 1. 明确在搜索引擎中索引数据包含哪些字段; 2.字段也会作为前端进行检索查询时候的关键词的参数名
    # document 可以对模型类中多个字段联合起来进行索引; use_template 以模板形式具体指明哪些字段作为索引
    text = indexes.CharField(document=True, use_template=True)

    # 下面是配合序列化器返回给前端,添加的字段
    id = indexes.IntegerField(model_attr='id')
    name = indexes.CharField(model_attr='name')
    price = indexes.DecimalField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    # 下面需要指明 这个索引是关联的那个模型类
    def get_model(self):
        return SKU

    # 不是所有的商品都需要建立索引,所以下面...
    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)





