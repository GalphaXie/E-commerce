from django.shortcuts import render

# Create your views here.


# url(r'^users/$', views.UserView.as_view()),
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import constants
from users.models import User
from users.serializers import UserAddressSerializer, AddressTitleSerializer, CreateUserSerializer, EmailSerializer, \
    UserDetailSerializer


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    serializer_class = CreateUserSerializer


# 分析: 接受前端通过正则校验过的数据,到数据库查询用户名的数量,返回给前端
# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """

    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """

    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }
        return Response(data)


# GET /user/  根据rest风格,本来要是 /users/<user_id>/  ,但是能进入个人中心,用户身份已经确定,采取了改复数为单数
class UserDetailView(RetrieveAPIView):
    '''用户的基本信息'''

    serializer_class = UserDetailSerializer
    # queryset = User.objects.all()

    permission_classes = [IsAuthenticated]  # 指明必须登录认证后才能访问

    def get_object(self):
        # 返回当前请求的用户
        # 在类视图对象中，可以通过类视图对象的属性获取request
        # 在django的请求request对象中，user属性表明当请请求的用户
        return self.request.user


# 　put /email/  <-  rest /users/<user_id>/email
class EmailView(UpdateAPIView):
    '''
    保存邮箱
    '''
    serializer_class = EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """
    邮箱验证
    这里可以采用 get 或 post 多种请求方式,但是这里采取 get 请求
    request参数:　token=?
    response参数: message
    """

    def get(self, request):
        # 接收参数
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)
        # 校验参数 token
        user = User.check_vertify_email_token(token)  # 校验token是属于 User模型的一个字段, 再借鉴User的封装的方法,我们可以自己定义模型类的方法

        if not user:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 如果token正常传递过来,那么激活成功,在数据库中进行标记 email_active
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})  # 返回成功


# 这里面导入的是 GenericViewSet, 而不是 GenericAPIView; 而且不用继承那么多 Mixin类; 如果不是 继承父类的方法,就不需要ModelMixin
class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    # 通过重写 get_queryset 的方法来提供查询集, 找到 request , 然后 再找到 user , 再找到 user属性
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """用户地址列表数据查询"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)  # 引入现成的地址序列化器来减少向前端返回数据的工作量,并指定为多个对象.形成嵌套.
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """修改用户地址"""
        # 检查用户地址数目不能超过上限
        count = request.user.addresses.count()  # 这里用了 模型类中 related_name='addresses'
        if count > constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '地址数量已达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        # return super().create(self, request, *args, **kwargs)
        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """删除操作"""
        # 不是真的删除
        address = self.get_object()
        # 进行逻辑删除
        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):  # 这里和下面的 pk=None 都不能省略
        """设置默认地址"""
        address = self.get_object()
        request.user.default_address = address
        request.user.save()  # 这里是保存的 user对象; 和上面保存 address 模型类有很大不同
        return Response({'message': 'OK'})

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()

        serializers = AddressTitleSerializer(instance=address, data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data)
