from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # 只有手机号是我们需要，而且默认没有的
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")  # 选项unique是必须的，其次 acquire=True默认

    class Meta:
        db_table = "tb_users"
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name