from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsSuperUser, IsOwner, CanModifyCartItem
#from rest_framework.generics import 
from .models import Category, Product, Order,Cart, CartItem, Subscription, FAQ
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, CartSerializer, CartItemSerializer, SubscriptionSerializer, FAQSerializer
from rest_framework.response import Response
from rest_framework import status
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
# Create your views here.



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "pk"
    cache_time = 60 * 60 * 24

    def list(self, request):
        data = cache.get('categories')
        if not data:
            data = self.serializer_class(self.get_queryset(), many=True).data
            cache.set('categories', data, self.cache_time)
        return Response(data, status=status.HTTP_200_OK)
    

    def retrieve(self, request, pk=None):
        data = cache.get('categories')
        if not data:
            data = self.serializer_class(self.get_queryset(), many=True).data
            cache.set('categories', data, self.cache_time)
            
            instance = self.queryset.get(pk=pk)
            if instance:
                instance = self.serializer_class(instance).data
        
        else:
            instance = next((item for item in data if item['id'] == int(pk)), None)

        if instance:
           return Response(instance, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_404_NOT_FOUND)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsSuperUser]
        
        return [permission() for permission in permission_classes]

class ProductViewSet(GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    lookup_field = 'pk'

    cache_time = 60 * 60 * 24



    def get_cache_key(self,request):
        category_id = request.query_params.get('category')
        if not category_id:
            category_id = "all"
        return f'category_id={category_id}'
 
    def list(self,request):
        cache_key = self.get_cache_key(request=request)
        data = cache.get(cache_key)
        if not data:
            filtered_queryset = self.filter_queryset(self.get_queryset())
            serializer = self.serializer_class(filtered_queryset, many=True)
            data = serializer.data

            if data:
                cache.set(cache_key, data, self.cache_time)

        return Response(data, status=status.HTTP_200_OK)
    
    def retrieve(self,request, pk=None):
        cached_data = cache.get("category_id=all")
        if cached_data:
            #  for item in cached_data:
            #      print(item['id'] ==  int(pk))
            instance = next((item for item in cached_data if item['id'] == int(pk)), None)

        else:
            serializer = self.serializer_class(self.queryset, many=True)
            cache.set('category_id=all', serializer.data, self.cache_time)
            instance = self.queryset.get(pk=pk)
        
        if instance:
            serializer = self.serializer_class(instance)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def update(self,request,pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            serializer = self.serializer_class(instance=instance,data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                cache.invalidate
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        return Response(status=status.HTTP_404_NOT_FOUND)
    

    def partial_update(self,request,pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            serializer = self.serializer_class(instance=instance,data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

        return Response(status=status.HTTP_404_NOT_FOUND)
    

    def destroy(self,request, pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsSuperUser]
        
        return [permission() for permission in permission_classes]



class OrderViewSet(GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def list(self,request):
        filtered_queryset = self.filter_queryset(queryset=self.queryset)
        serializer = self.serializer_class(filtered_queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    

    def retrieve(self,request, pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            serializer = self.serializer_class(instance)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_404_NOT_FOUND) 

    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self,request, pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            serializer = self.serializer_class(instance=instance,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def partial_update(self, request,pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            serializer = self.serializer_class(instance=instance,data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    def destroy(self,request,pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = IsAuthenticated
        else:
            permission_classes = [IsOwner | IsSuperUser]
        
        return [permission() for permission in permission_classes]
    

class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [CanModifyCartItem | IsSuperUser]

    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        serializer.save(cart=cart)




class CartViewSet(GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = Cart.objects.filter(user=self.request.user)

    def list(self, request):
        cart = Cart.objects.get(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    


    def destroy(self,request):
        ...
    


    

class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer



class FAQViewSet(ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer