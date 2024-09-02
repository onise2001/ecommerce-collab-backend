from django.db import models
from django.contrib.auth.models import AbstractUser
import random, string
from datetime import  timedelta
from django.utils import timezone

# Create your models here.

def generate_recovery_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


class CustomUser(AbstractUser):
    profilePicture = models.ImageField()



class PasswordRecovery(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recovery_code = models.CharField(max_length=6, default=generate_recovery_code,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)  # Expires in 5 minutes
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at