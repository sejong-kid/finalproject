from django.db import models

# Create your models here.
class Article(models.Model):
    site_name = models.CharField(max_length=200)
    title= models.CharField(max_length=1000, null=True)
    detail= models.TextField(null=True)
    updated = models.CharField(max_length=20)
    file = models.CharField(max_length=10, null=True)
    href = models.CharField(max_length=1000, null=True)
    title_noun = models.CharField(max_length=5000, null=True)
    content_noun = models.CharField(max_length=5000, null=True)