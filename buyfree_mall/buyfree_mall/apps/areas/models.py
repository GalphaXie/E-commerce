from django.db import models


# Create your models here.

class Area(models.Model):
    """
    行政区划
    1. 自关联字段的外键指向自身，所以ForeignKey('self')
    2. 需要使用related_name指明查询一个行政区划的所有下级行政区划时，使用哪种语法查询，如本模型类中指明通过Area模型类对象.subs查询所有下属行政区划，
    而不是使用Django默认的Area模型类对象.area_set语法。
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    # 自关联:外键字段就是自己的主键; 必须设置on_delete字段且常量是models的,且不要调用成models.SET_NULL()方法
    # related_name 指定的是 嵌套的 子级 的模型类(体现1-n, 而subs体现自关联  类似flask中的 backref)
    # 因为省级 对应的不存在 其父级 ,所以 可以为空;  blank只是在填写表单的时候可以为空，而在数据库上存储的是一个空字符串；null是在数据库上表现NULL，而不是一个空字符串；这blank可以不写
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True,
                               verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = verbose_name

    # 这个方法在后面写子类模型化类的时候会用到
    def __str__(self):
        return self.name
