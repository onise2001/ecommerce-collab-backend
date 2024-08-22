from rest_framework import serializers
from .models import CustomUser
from ecommerce_api.models import Cart
from ecommerce_api.serializers import CartSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    cart = CartSerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'profilePicture', 'is_superuser' , 'cart']
        extra_kwargs = {'password': {"write_only": True}, 'is_superuser':{'read_only': True}, 'id':{'read_only': True}}


    
    def create(self,validated_data):
        password = validated_data.pop('password')
        new_user = CustomUser(**validated_data)
        new_user.set_password(password)
        new_user.save()
        Cart.objects.create(user=new_user)
        return new_user