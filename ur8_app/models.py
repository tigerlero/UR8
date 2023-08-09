# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="avatars", default="avatar/None/default_avatar.png")
    notifications = models.CharField(default="Welcome", max_length=4000000)
    count = models.IntegerField(default=0)
    subscribes = models.CharField(default="", max_length=40000)
    subscribers = models.CharField(default="", max_length=40000)
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
    voice_language = models.TextField(max_length=2, default="el")
    subtitles_language = models.TextField(max_length=2, default="el")
    avg_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
    rating_counter = models.IntegerField(default=0)
    thumbnail = models.FileField(upload_to="thumbnails", default="thumbnail/None/default_thumb.png")
    th = models.BooleanField(default=True)
    # thumbnails will be uploaded to: 'uploads/media/thumbnails'
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