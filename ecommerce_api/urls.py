from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryViewSet, OrderViewSet, CartViewSet, CartItemViewSet, OrderItemViewSet, SubscriptionViewSet, FAQViewSet, MayAlsoLike, PopularWith, AddressViewSet,ReviewViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'product', ProductViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'order', OrderViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-item', CartItemViewSet)
router.register(r'order-item', OrderItemViewSet)
router.register(r'subscription', SubscriptionViewSet)
router.register(r'faq', FAQViewSet)
router.register(r'address', AddressViewSet)
router.register(r'reviews', ReviewViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('also-like/', MayAlsoLike.as_view()),
    path('popular-with/', PopularWith.as_view()),

]
