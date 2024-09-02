from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser, PasswordRecovery
from .serializers import CustomUserSerializer, PasswordRecoverySerializer
from .permissions import CanRetrieveUsers, CanModifyUser
from ecommerce_api.permissions import IsSuperUser
from .filters import CustomUserFilter
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
# Create your views here.

class CustomUserViewSet(GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer



    def list(self, request):
        serializer = self.serializer_class(self.queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


    def retrieve (self,request,pk=None):
        instance = self.queryset.get(pk=pk)
        if instance:
            serializer = self.serializer_class(instance)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

 
    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self,request,pk=None):
        instance = self.queryset.get(pk=pk)

        if instance :
            serializer = self.serializer_class(instance=instance, data=request.data)
            if serializer.is_valid():
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self,request,pk=None):
        instance = self.queryset.get(pk=pk)

        if instance :
            serializer = self.serializer_class(instance=instance, data=request.data, partial=True)
            if serializer.is_valid():
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self,request,pk=None):
        instance = self.queryset.get(pk=pk)

        if instance :
            instance.delete()            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        return Response( status=status.HTTP_400_BAD_REQUEST)
    

    def get_permissions(self):
        if self.action in ['list','destroy']:
            permission_classes = [IsSuperUser]
        elif self.action == 'retrieve':
            permission_classes = [CanRetrieveUsers]

        elif self.action in ['update', 'partial_update']:
            permission_classes = [CanModifyUser]
        
        else:
            permission_classes = []

        return [permission() for permission in permission_classes]
    




class CustomUserViewForUser(GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    #filter_backends = [CustomUserFilter]

    def list(self, request):
        serializer = self.serializer_class(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    

    

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [CanModifyUser]
        
        return [permission() for permission in permission_classes]
    




class RestorePassword(GenericViewSet):
    serializer_class = PasswordRecoverySerializer

    def create(self,request):
        user = get_object_or_404(CustomUser,username=request.data.get('username'))

        recover = PasswordRecovery.objects.create(user=user)
        send_mail(
            'Password Recovery Code',
            f'Your password recovery code is: {recover.recovery_code}',
            recipient_list=[user.email],
            from_email='babulashvili.vaja@gmail.com',
            fail_silently = False
        )
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='validate_code')
    def validate_code(self,request):
        recovery_instance = get_object_or_404(PasswordRecovery,recovery_code=request.data.get('recovery_code'))
        return Response(status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='change_password')
    def change_password(self,request):
        recovery_instance = get_object_or_404(PasswordRecovery,recovery_code=request.data.get('recovery_code'))
        recovery_instance.user.set_password(request.data.get('password'))
        recovery_instance.user.save()

        return Response(status=status.HTTP_200_OK)
    
