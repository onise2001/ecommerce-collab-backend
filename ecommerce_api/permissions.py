from rest_framework.permissions import BasePermission



class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
        return False


# class CanAddToCart(BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.user.is_authenticated:
#             if request.user == obj.user:
#                 return True
            
#         return False
    


class CanModifyCartItem(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user == obj.cart.user:
                return True
            
        return False
    
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request. user == obj.user:
                return True
            
        return False