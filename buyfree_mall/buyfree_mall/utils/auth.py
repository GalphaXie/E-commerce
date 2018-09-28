"""
跨站请求伪造和跨域资源共享的区别
"""

from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class MyJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        print('authenticate')
        try:
            return super().authenticate(request)
        except Exception:
            return None
