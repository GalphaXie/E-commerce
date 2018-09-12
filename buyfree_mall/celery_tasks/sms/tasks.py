# -*- coding: utf-8 -*-
# @File : tasks.py
# @Author : Xie
# @Date   : 9/10/18
# @Desc   : 任务函数所在的模块(建议名称为tasks) 默认
import logging

from .utils.yuntongxun.sms import CCP
from celery_tasks.main import celery_app

logger = logging.getLogger('django')


@celery_app.task(name='send_sms_code')  # 这里task是单数; 通过name参数来指定任务的名字
def send_sms_code(mobile, sms_code, expires, temp_id):
    '''
    发送短信验证码
    :return: 不需要决定返回值,这里由Django那边返回
    '''
    # 发送短信验证码
    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, expires], temp_id)  # 注意： 测试的短信模板编号为1
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
