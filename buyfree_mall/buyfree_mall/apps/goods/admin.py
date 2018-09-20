from django.contrib import admin

# Register your models here.
from goods import models


# @admin.register(models.SKU)  # 方式二
class SKUAdmin(admin.ModelAdmin):
    """
    实现 异步 任务
    """

    def save_model(self, request, obj, form, change):
        """
        在Admin站点保存或删除数据时，Django是调用的Admin站点管理器类的save_model()方法和delete_model()方法，我们只需重新实现这两个方法，
        在这两个方法中调用异步任务即可。
        :param request: 视图的请求对象
        :param obj: 数据对应的模型类对象,还没有保存到数据库中, 重点就是这个 参数
        :param form: 原始的表单数据放在form
        :param change: 发生数据改变的地方
        :return:
        """
        obj.save()
        # 接下来实现异步任务
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)

    # # 删除的话没必要重新生成到页面,所以这里可以不写
    # def delete_model(self, request, obj):
    #     """
    #
    #     :param request: 请求删除的request对象
    #     :param obj: 当前要删除的对象
    #     :return:
    #     """
    #     obj.delete()


class SKUSpecificationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        # obj -> SKUImage 对象

        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku

        if not sku.default_image_url:
            # http://image.meiduo.site:8888/groupxxxxxx
            # default_image_url 对应的字段是 CharField ,是一个完整的 url
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)  # 这里加入自定义的admin模型类,是两种方式中的一种;另外一种是装饰器
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)
