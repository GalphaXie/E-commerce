from django.conf import settings
from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer

from users import constants


class User(AbstractUser):
    # 只有手机号是我们需要，而且默认没有的
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")  # 选项unique是必须的，其次 acquire=True默认
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

    # Django中提供了email字段,但是数据库中没有激活状态的字段,is_active用来 表示 用户的逻辑删除

    class Meta:
        db_table = "tb_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        '''
        使用 itsdangerous 子类方法
        :return:
        '''

        # 序列化器 创建 (配置.key, 过期时间)
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        # 设置 payload 中的数据
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()  # bytes字符串 -> 解码
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token  # 拼接
        return verify_url
