from django.db import models

class Post(models.Model):
    text = models.CharField(max_length=200)
    date = models.DateTimeField('date published')
