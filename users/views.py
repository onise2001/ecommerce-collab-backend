from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser 
from .serializers import CustomUserSerializer
from .permissions import CanRetrieveUsers, CanModifyUser
from ecommerce_api.permissions import IsSuperUser

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
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
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