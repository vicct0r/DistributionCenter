from django.db import models
from django.urls import reverse

from django.template.defaultfilters import slugify


class Base(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class Product(Base):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    slug = models.SlugField(null=True)

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)