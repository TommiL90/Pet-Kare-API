from django.db import models
from pets.models import Pet


class Trait(models.Model):
    name = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    pets = models.ManyToManyField(Pet, related_name="traits")
