from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from .models import Product, Category


class CategoryAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent_cat', 'total_views', )


class CategoryParentSerializer(serializers.Serializer):
    parent_name = serializers.CharField(max_length=255)
    parent_id = serializers.IntegerField()
    grand_name = serializers.CharField(max_length=255)
    grand_id = serializers.IntegerField()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

