from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomUserViewSet, CustomUserViewForUser, RestorePassword
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'signup', CustomUserViewSet)
router.register(r'users', CustomUserViewForUser, basename='users')
router.register(r'recover',RestorePassword, basename='recover' )

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view())    
]
