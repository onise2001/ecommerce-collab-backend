from rest_framework import serializers
from .models import Category, Product, Order, OrderItem,Cart, CartItem, Subscription, FAQ, Address
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



class OrderItemSerializer(WritableNestedModelSerializer):
    product = ProductSerializer(read_only=True, )
    product_id = serializers.PrimaryKeyRelatedField(
            queryset=Product.objects.all(),
            write_only=True,
            source="product"
        )
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_kwargs = { 'order':{'read_only': True}}



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    class Meta:
        model = Order
        fields = ['id','recipientName','recipientPhoneNumber','dateOfDelivery','deliveryTime','street','houseNumber','total','user', 'items' ]
        extra_kwargs = { 'user': {'read_only':True}}

    
    def create(self,validated_data):
        order_items = validated_data.pop('items')
        new_order = super().create(validated_data)

        for item in order_items:
            OrderItem.objects.create(order=new_order, **item)
        
        
        return new_order
    

class SubscriptionSerializer(serializers.ModelSerializer):
    delivery = serializers.CharField(read_only=True)
    class Meta:
        model = Subscription
        fields = '__all__'



class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'




class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'city','houseNumber', 'street', 'note']
        extra_kwarg = {'user': {'read_only': True}}