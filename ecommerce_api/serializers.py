from rest_framework import serializers
from .models import Category, Product, Order, OrderItem,Cart, CartItem
from drf_writable_nested.serializers import WritableNestedModelSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    


class ProductSerializer(WritableNestedModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        source='category'
    )
    class Meta:
        model = Product
        fields = '__all__'



class CartItemSerializer(WritableNestedModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        source="product"
    )
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        extra_kwargs = {'id': {'read_only': True}}



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = '__all__'




class OrderItemSerializer(serializers.ModelSerializer):
    product = CartItemSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
            queryset=CartItem.objects.all(),
            write_only=True,
            source="product"
        )
    class Meta:
        model = OrderItem
        fields = '__all__'



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    class Meta:
        model = Order
        fields = '__all__'