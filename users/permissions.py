from rest_framework.permissions import BasePermission



class CanRetrieveOrListUsers(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user == obj or request.user.is_superuser

        return False
    
class CanModifyUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user == obj
        return  False


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser
        return False