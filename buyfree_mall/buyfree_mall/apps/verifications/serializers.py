from django_redis import get_redis_connection
from rest_framework import serializers


class ImageCodeCheckSerializer(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)  # 默认acquire=True

    def validate(self, attrs):  # 一次校验多个,选取validate而不是validate_data
        """
        校验
        """
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        # 查询真实图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')  # 抛出异常,而不需要 return

        # 删除图片验证码 : 防止恶意尝试破解图片验证码;保证每张 只能 使用一次
        redis_conn.delete('img_%s' % image_code_id)

        # 比较图片验证码
        real_image_code_text = real_image_code_text.decode()  # 字节转换
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        # 判断是否在60s内
        # get_serializer 方法在创建序列化器对象的时候,会补充context属性
        # context属性包括三个值, request, format, view 类视图对象
        # 类视图对象:  self.context['view']

        # Django的类视图对象中,kwargs属性保存了路径提取出来的参数

        mobile = self.context['view'].kwargs['mobile']
        # 后端也要记录和控制'倒计时',防止前端绕过正常方式来访问'
        send_flag = redis_conn.get("send_flag_%s" % mobile)  # 如果过期,表示'没有发送过',可以再次发送
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')

        return attrs
