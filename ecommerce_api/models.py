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


class Cart(models.Model):
    user = models.ForeignKey(to=('users.CustomUser'), on_delete=models.CASCADE)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.FloatField()




class Order(models.Model):
    recipientName = models.CharField(max_length=255)
    recipientPhoneNumber = models.CharField(max_length=50)
    dateOfDelivery  = models.DateField()
    deliveryTime = models.TimeField()
    street = models.CharField(max_length=255)
    houseNumber = models.CharField(max_length=10)
    total = models.FloatField()
    user = models.ForeignKey(to=('users.CustomUser'), on_delete=models.CASCADE)



class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    quantity = models.FloatField()



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




class Address(models.Model):
    city = models.CharField(max_length=255)
    houseNumber = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    user = models.OneToOneField(to="users.CustomUser", on_delete=models.CASCADE, related_name="address")






@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache_key = 'categories'
    cache.delete(cache_key)



@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete(f'category_id={instance.category.id}')
    cache.delete('category_id=all')



@receiver(post_save, sender=Order)
@receiver(post_delete, sender=Order)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete(f'order_user_{instance.user.id}')
  