from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from rest_framework.generics import ListAPIView
from rest_framework.permissions import SAFE_METHODS, IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import IsSuperUser, IsOwner, CanModifyCartItem
#from rest_framework.generics import 
from .models import Category, Product, Order,Cart, CartItem , OrderItem, Subscription, FAQ
from .serializers import CategorySerializer, ProductSerializer, OrderSerializer, CartSerializer, CartItemSerializer , OrderItemSerializer, SubscriptionSerializer, FAQSerializer
from rest_framework.response import Response
from rest_framework import status
from .filters import ProductFilter, OrderFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
import random
# Create your views here.



# Test OrderViewSet Thoroughly, add permissions on FAQ and Subscription ViewSets, add filters on orderviewset so user sees only their orders, ask chatgpt if what i am doint with CustomUserViewSetForUSers is a good approach


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
            instance = next((item for item in cached_data if item['id'] == int(pk)), None)

        else:
            serializer = self.serializer_class(self.queryset, many=True)
            cache.set('category_id=all', serializer.data, self.cache_time)
            instance = self.queryset.get(pk=pk)
            if instance:
                serializer = self.serializer_class(instance)
                instance = serializer.data
        
        if instance:
            return Response(data=instance, status=status.HTTP_200_OK)

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



class OrderViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [OrderFilter]
    lookup_field = 'pk'

    cache_time = 60 * 60
    cache_key ='orders_user_'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}



    def list(self,request):
        orders = cache.get(f'{self.cache_key}{request.user.id}')

        if not orders:
            queryset = self.filter_queryset(queryset=self.queryset)
            serializer = self.serializer_class(queryset,)
            orders = serializer.data
            cache.set(f'orders_user_{request.user.id}', orders, self.cache_time)

        return Response(data=orders, status=status.HTTP_200_OK)
    

    def retrieve(self,request, pk=None):
        orders = cache.get(f'{self.cache_key}{request.user.id}')

        if not orders:
            orders = self.serializer_class(self.queryset, many=True)
            cache.set(f'{self.cache_key}{request.user.id}', orders.data, self.cache_time)

            instance = self.queryset.get(pk=pk)
            if instance:
                serializer = self.serializer_class(instance)
                instance = serializer.data
            
        else:
            instance = next((item for item in orders if item['id'] == int(pk)), None)
            
            
        if instance:
            return Response(data=instance, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND) 

    
    
    
    def create(self,request):
        print(request.user.id)
        serializer = self.serializer_class(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            self.perform_create(serializer)
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
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsOwner | IsSuperUser]
        
        return [permission() for permission in permission_classes]
    


class OrderItemViewSet(GenericViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = "pk"


    def list(self,request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    

    def retrieve(self,request,pk=None):
        instance = self.get_object()
        if instance:
            serializer = self.serializer_class(instance)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    def update(self,request, pk=None):
        instance = self.get_object()

        if instance:
            serializer = self.serializer_class(instance=instance, data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self,request, pk=None):
        instance = self.get_object()

        if instance:
            serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)


    def destroy(self,request,pk=None):
        instance = self.get_object()

        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_404_NOT_FOUND)
    

class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [CanModifyCartItem | IsSuperUser]

    def perform_create(self, serializer):
        cart = Cart.objects.get(user=self.request.user)
        serializer.save(cart=cart)
        cache.delete(f'cart_{self.request.user.id}') 

    
    def perform_update(self, serializer):
        super().perform_update(serializer)
        cache.delete(f'cart_{self.request.user.id}') 

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        cache.delete(f'cart_{self.request.user.id}')  




class CartViewSet(GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    cache_time = 60 * 60

    def list(self, request):
        cache_key = f'cart_{self.request.user.id}'
        cart = cache.get(cache_key)
        if not cart:
            cart,_ = Cart.objects.get_or_create(user=request.user)
            cart = self.get_serializer(cart).data
            cache.set(cache_key, cart, self.cache_time )

        
        
        return Response(data=cart, status=status.HTTP_200_OK)
        
    
    

    def destroy(self,request):
        ...
    


class MayAlsoLike(ListAPIView):
    serializer_class = ProductSerializer
    
    def list(self, request, *args, **kwargs):
        data = cache.get('category_id=all')
        cache_time = 60 * 60 * 24

        if not data:
            products = Product.objects.all()
            serializer = self.serializer_class(products, many=True)
            data = serializer.data
            cache.set('category_id=all', data, cache_time)

       # data = list(data)

        if len(data) >= 4:
            random.shuffle(list(data))
            response = data[:1]
        else:
            response = data
        
        return Response(data=response, status=status.HTTP_200_OK)
        


class PopularWith(ListAPIView):
    def list(self, request, *args, **kwargs):
        data = cache.get('category_id=all')
        cache_time = 60 * 60 * 24

        if not data:
            products = Product.objects.all()
            serializer = self.serializer_class(products, many=True)
            data = serializer.data
            cache.set('category_id=all', data,cache_time)


        #data = list(data)
        
        if len(data)> 10:
            random.shuffle(list(data))
            response = data[:10]
        else: 
            response = data
        
        return Response(data=response, status=status.HTTP_200_OK)

    

class SubscriptionViewSet(ModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer



class FAQViewSet(ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer