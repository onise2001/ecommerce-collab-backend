from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField()


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    inStock = models.IntegerField()
    image = models.ImageField()


class Order(models.Model):
    recipientName = models.CharField(max_length=255)
    recipientPhoneNumber = models.CharField(max_length=50)
    dateOfDelivery  = models.DateField()
    deliveryTime = models.TimeField()
    street = models.CharField(max_length=255)
    houseNumber = models.CharField(max_length=10)
    total = models.FloatField()
    user = models.ForeignKey(to=('users.CustomUser'), on_delete=models.CASCADE)

class Cart(models.Model):
    user = models.ForeignKey(to=('users.CustomUser'), on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()

class OrderItem(models.Model):
    product = models.ForeignKey(Product, related_name='items' ,on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)



# class Review(models.Model):
#     text = models.TextField()
#     user = 


class Subscription(models.Model):
    image = models.ImageField()
    category = models.CharField(max_length=100)
    price = models.FloatField()
    delivery = models.TextField(default="Free Delivery")
    theBest = models.TextField()
    firstDelivery = models.TextField(blank=True) 
    firstDelivery2 = models.TextField(blank=True)
    saveUp = models.FloatField()


class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()






@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache_key = 'categories'
    cache.delete(cache_key)



@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete('category_id=all')
    for category in Category.objects.all():
        cache.delete(f'category_id={category.id}')