from  rest_framework.filters import BaseFilterBackend 
import django_filters 
from .models import Product

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.NumberFilter(field_name='category__id')


    class Meta:
        model = Product
        fields = ['search', 'category']


class OrderFilter(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(user=request.user)
        return queryset


    # def filter_queryset(self, request, queryset, view):
    #     search = request.query_params.get('search')
    #     category = request.query_params.get('category')
    #     price = request.query_params.get('price')


    #     if search:
    #         queryset = queryset.filter(name__contains=search.lower())

    #     if category and category.isdigit():
    #         queryset = list(filter(lambda x:  x['category']['id'] == int(category), queryset))

    #     if price and price.isdigit():
    #         queryset = queryset.filter(price__lt=float(price))

        
    #     return queryset


