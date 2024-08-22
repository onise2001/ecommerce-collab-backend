from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, CartViewSet, CartItemViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'product', ProductViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'order', OrderViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-item', CartItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
