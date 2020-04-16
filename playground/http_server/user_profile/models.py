"""
Holds the models that django will use to populate
the forms
"""
from django.db import models

class Post(models.Model):
    """Posts from users"""
    text = models.CharField(max_length=200)
    date = models.DateTimeField('date published')

class Followers(models.Model):
    """Followers list"""
    name = models.CharField(max_length=200)
    dateAdded = models.DateTimeField('date follower added')

class Following(models.Model):
    """Following list"""
    name = models.CharField(max_length=200)
    dateAdded = models.DateTimeField('date follower added')

    def __str__(self):
        return self.name
