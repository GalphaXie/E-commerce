from rest_framework import serializers

from carts.serializers import CartSKUSerializer


class OrderSettlementSerializer(serializers.ModelSerializer):
    # max_digits 包含小数的最多位数，decimal_places 几位小数
    freight = serializers.DecimalField(max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True, read_only=True)