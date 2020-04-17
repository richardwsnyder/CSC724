"""
Holds the models that django will use to populate
the forms
"""
from django.db import models

class Post(models.Model):
    """Posts from this user"""
    text = models.CharField(max_length=200)
    date = models.DateTimeField('date published')

class FeedPost(models.Model):
    """Posts from any users"""
    text = models.CharField(max_length=200)
    date = models.DateTimeField('date published')
    fullname = models.CharField(max_length=64)
    username = models.CharField(max_length=32)

class Followers(models.Model):
    """Followers list"""
    name = models.CharField(max_length=200)
    dateAdded = models.DateTimeField('date follower added')

    def __str__(self):
        return self.name

class Following(models.Model):
    """Following list"""
    name = models.CharField(max_length=200)
    dateAdded = models.DateTimeField('date follower added')

    def __str__(self):
        return self.name
