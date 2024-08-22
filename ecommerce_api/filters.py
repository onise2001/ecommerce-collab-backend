from  rest_framework.filters import BaseFilterBackend 
from .models import Product

class ProductFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search = request.query_params.get('search')
        category = request.query_params.get('category')
        price = request.query_params.get('price')


        if search:
            queryset = queryset.filter(name__contains=search.lower())

        if category and category.isdigit():
            queryset = queryset.filter(category__id=category)

        if price and price.isdigit():
            queryset = queryset.filter(price__lt=float(price))

        
        return queryset