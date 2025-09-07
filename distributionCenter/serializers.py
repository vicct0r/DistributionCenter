from rest_framework import serializers
from .models import Product


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['created', 'modified', 'is_active', 'name', 'price', 'quantity', 'slug']
        extra_kwargs = {
            'created': {'read_only': True},
            'modified': {'read_only': True},
            'is_active': {'read_only': True},
            'slug': {'read_only': True}
        }


class ProductTradeSerializer(serializers.Serializer):
    product = serializers.CharField()
    quantity = serializers.IntegerField()