#!/home/richard/.virtualenvs/djp/bin/python
"""
功能：手动生成所有SKU的静态detail html文件
使用方法:
    ./regenerate_index_html.py
    # 注意要给该文件添加 执行 权限 , chmod +x regenerate_index_html.py
"""

import sys
sys.path.insert(0, '../')


import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'buyfree_mall.settings.dev'

# 让Django进行初始化配置
import django
django.setup()


from contents.crons import generate_static_index_html

if __name__ == '__main__':
    generate_static_index_html()
