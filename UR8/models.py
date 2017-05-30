# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.contrib.postgres.fields import ArrayField


class Profile(models.Model):
    user = models.OneToOneField(User)
    image = models.ImageField(upload_to="avatars", default="avatar/None/default_avatar.png")
    notifications = models.CharField(default="", max_length=4000000)
    count = models.IntegerField(default=0)
    subscribes = models.CharField(default="", max_length=40000)
    # images will be uploaded to: 'uploads/media/avatars'

    def __str__(self):
        return self.user.username


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.FileField(upload_to="videos")
    # videos will be uploaded to: 'uploads/media/videos'
    title = models.CharField(max_length=46)
    tags = models.CharField(default="", max_length=200)
    description = models.TextField(max_length=3000)
    avg_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    rating_counter = models.IntegerField(default=0)
    thumpnail = models.FileField(upload_to="thumpnails", default="thumpnail/None/default_thump.png")
    # thumpnails will be uploaded to: 'uploads/media/thumpnails'
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username+" "+self.title+" "+self.description


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000, default="no-review")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=1.0)
    approvedBy = models.TextField(default="")
    disapprovedBy = models.TextField(default="")

    def __str__(self):
        return self.user.username+" "+self.text
