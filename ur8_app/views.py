# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from .forms import UserRegFrom, EditAvatarForm, ResetPasswordForm, UploadVideoForm, UpdateVideoForm
from .models import Profile, Video, Review
from django.contrib.auth.models import User
from django.http import HttpResponse
from moviepy.editor import *
import os
import json
import time
from django.http import JsonResponse
from gtts import gTTS
from django.db import connection

def text_to_speech(text, language='el', output_file='output.mp3'):
    tts = gTTS(text=text, lang=language)
    tts.save(output_file)


from django.views.decorators.http import require_POST
from PIL import Image


def check_username(request):
    username = request.POST.get('username')
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("This username already exists")
    else:
        return HttpResponse("")


def handler400(request, exception):
    return render(request, '400.html', status=400)


def handler403(request, exception):
    return render(request, '403.html', status=403)


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def home(request):
    videos = Video.objects.all()
    users = User.objects.all()
    video_results = []
    new = []
    popular = []
    best = []
    if Video._meta.db_table in connection.introspection.table_names():
        for video in videos:
            video_results.append(video)
            new.append(video)
            popular.append(video)
            best.append(video)
    video_results = video_results[-29:]
    new = new[-29:]
    popular = popular[-29:]
    best = best[-29:]
    video_results = sort_videos(video_results, 4, 12, 5)
    new = sort_videos(new, 10, 6, 1)
    popular = sort_videos(popular, 1, 6, 10)
    best = sort_videos(best, 1, 17, 2)
    hasRes = False
    if len(video_results) >= 1:
        hasRes = True
    else:
        hasRes = False
    if request.method == 'GET' and request.user.is_authenticated:
        return render(request, 'home.html',
                      {'video_results': video_results, 'hasRes': hasRes, 'new': new, 'popular': popular, 'best': best,
                       'users': users})
    else:
        return render(request, 'home.html',
                      {'video_results': video_results, 'hasRes': hasRes, 'new': new, 'popular': popular, 'best': best,
                       'users': users})


def sort_videos(videos, id_mod, avg_mod, video_mod):
    overall = [0] * 30
    # calculate overall score
    for i, video in enumerate(videos):
        overall[i] += id_mod * video.id
        overall[i] += avg_mod * video.avg_rating
        overall[i] += video_mod * video.views
    # insertion sort for overall score
    for i in range(1, len(videos)):
        j = i
        while (j > 0) and (overall[j] > overall[j - 1]):
            videos[j], videos[j - 1] = videos[j - 1], videos[j]
            overall[j], overall[j - 1] = overall[j - 1], overall[j]
            j -= 1
    return videos


def channel(request, channel_slug):
    user = User.objects.get(username=channel_slug)
    users = User.objects.all()
    videos = user.video_set.all()
    if request.method == 'GET':
        hasRes = False
        if len(videos) >= 1:
            hasRes = True
        else:
            hasRes = False
        for video in videos:
            video.tags = video.tags.split(',')
            video.tags.pop()
        return render(request, 'channel.html', { 'hasRes': hasRes, 'videos': videos, 'user': user, 'users': users})
    else:
        return render(request, 'home.html', {'users': users})


def channels(request):
    users = User.objects.all()
    if request.method == 'GET':
        return render(request, 'channels.html', {'users': users})
    else:
        return render(request, 'home.html', {'users': users})


def edit_review(request, video_id, review_id):
    users = User.objects.all()

    if request.method == 'GET' and request.user.is_authenticated:
        review = Review.objects.get(id=review_id)
        video = Video.objects.get(id=video_id)
        video_id = video.id
        return render(request, 'edit_review.html', {'review': review, 'video_id': video_id, 'users': users})

    elif request.method == 'POST' and request.user.is_authenticated:
        newText = request.POST['text']
        newVal = int(request.POST['rating'])  # new rating
        video = Video.objects.get(id=video_id)
        review = Review.objects.get(id=review_id)

        # remove old rating
        old_avg = float(video.avg_rating)
        rating = float(review.rating)
        count = float(video.rating_counter)
        new_avg = 0.0
        if (count - 1) > 0:
            new_avg = ((old_avg * count) - rating) / (count - 1)

        video.avg_rating = new_avg
        video.rating_counter -= 1
        video.save()

        # save changes
        review.text = newText
        review.rating = newVal
        review.save()

        # add new rating
        video.rating_counter += 1
        old_avg2 = video.avg_rating
        count2 = video.rating_counter
        video.avg_rating = (old_avg2 * (count2 - 1) + newVal) / count2
        video.save()

        # data = {'ok': 'yes'}
        # return HttpResponse(json.dumps(data), content_type='application/json')
        context = {
            'review_id': review.id,
            'video_id': video.id,
            "src": review.user.profile.image,
            'text': review.text,
            "uname": review.user.username,
            "rating": review.rating,
            "like": review.approvedBy.count(","),
            'dislike': review.disapprovedBy.count(","),
            'ID': review.id
        }
        return render(request, 'review.html', context)


def delete_review(request, review_id, video_id):
    if request.method == 'POST' and request.user.is_authenticated:
        review = Review.objects.get(id=review_id)
        video = Video.objects.get(id=video_id)
        # average = ((average * nbValues) - value) / (nbValues - 1)
        old_avg = float(video.avg_rating)
        rating = float(review.rating)
        count = float(video.rating_counter)
        new_avg = 0.0
        if (count - 1) > 0:
            new_avg = ((old_avg * count) - rating) / (count - 1)
        video.avg_rating = new_avg
        video.rating_counter -= 1
        video.save()
        review.delete()
        print("deleted")
        context = {
            'review_id': review.id,
            'video_id': video.id,
            "src": review.user.profile.image,
            'text': review.text,
            "uname": review.user.username,
            "rating": review.rating,
            "like": review.approvedBy.count(","),
            'dislike': review.disapprovedBy.count(","),
            'ID': review.id
        }
        return render(request, 'review_edit.html', context)


def like_review(request, review_id):
    if request.method == 'GET':
        review = Review.objects.get(id=review_id)
        uname = request.user.username
        if (uname in review.approvedBy):
            context = {
                'like': review.approvedBy.count(","),
                'review_id': review,
                'dislike': review.disapprovedBy.count(",")
            }
            return render(request, 'updated_buttons.html', context)
            # return JsonResponse({'like': review.approvedBy.count(",")})
        else:
            # Like the review
            review.approvedBy += uname + ","
            if uname in review.disapprovedBy:
                review.disapprovedBy = review.disapprovedBy.replace(uname + ",", "")
            review.save()
            context = {
                'like': review.approvedBy.count(","),
                'review_id': review.id,
                'dislike': review.disapprovedBy.count(",")
            }
            # return JsonResponse({'like': review.approvedBy.count(",")})
            return render(request, 'updated_buttons.html', context)


def dislike_review(request, review_id):
    if request.method == 'GET':
        review = Review.objects.get(id=review_id)
        uname = request.user.username
        if (uname in review.disapprovedBy):
            context = {
                'like': review.approvedBy.count(","),
                'review_id': review.id,
                'dislike': review.disapprovedBy.count(",")
            }
            # return JsonResponse({'like': review.approvedBy.count(",")})
            return render(request, 'updated_buttons.html', context)
        else:
            # Dislike the review
            review.disapprovedBy += uname + ","
            if uname in review.approvedBy:
                review.approvedBy = review.approvedBy.replace(uname + ",", "")
            review.save()
            context = {
                'like': review.approvedBy.count(","),
                'review_id': review.id,
                'dislike': review.disapprovedBy.count(",")
            }
            # return JsonResponse({'like': review.approvedBy.count(",")})
            return render(request, 'updated_buttons.html', context)


def update_review(request, review_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        review = Review.objects.get(id=review_id)
        uname = request.user.username

        # Check if the request is for like or dislike
        action = data.get('action', None)
        if action == 'like':
            if uname in review.approvedBy:
                review.approvedBy = review.approvedBy.replace(uname + ",", "")
            else:
                review.approvedBy += uname + ","
                if uname in review.disapprovedBy:
                    review.disapprovedBy = review.disapprovedBy.replace(uname + ",", "")
        elif action == 'dislike':
            if uname in review.disapprovedBy:
                review.disapprovedBy = review.disapprovedBy.replace(uname + ",", "")
            else:
                review.disapprovedBy += uname + ","
                if uname in review.approvedBy:
                    review.approvedBy = review.approvedBy.replace(uname + ",", "")

        review.save()

        # Get the updated like and dislike counts
        like_count = review.approvedBy.count(",")
        dislike_count = review.disapprovedBy.count(",")

        # Return the updated button content as JSON response
        response_data = {'like': like_count, 'dislike': dislike_count}
        return HttpResponse(json.dumps(response_data), content_type='application/json')


def rated_video(request, video_id):
    if request.method == 'POST' and request.POST.get('rated') == 'yes':
        video = get_object_or_404(Video, id=video_id)
        text = request.POST.get('text', '')  # Use get() with a default value to handle missing 'text' key
        rating = int(request.POST.get('rating', 0))  # Use get() with a default value to handle missing 'rating' key

        review = Review(user=request.user, video=video, text=text, rating=rating)
        review.save()

        video.rating_counter += 1
        # Calculate new average rating using the formula: (previous_mean * (count - 1) + new_value) / count
        old_avg = video.avg_rating
        count = video.rating_counter
        video.avg_rating = (old_avg * (count - 1) + rating) / count
        video.save()

        response_data = {'ok': 'yes'}  # You can customize the response data as needed
        return JsonResponse(response_data)


# view a specific uploaded video
def s_vid(request, video_id):
    users = User.objects.all()
    if request.method == 'GET':
        video = Video.objects.get(id=video_id)
        videos = Video.objects.all()
        user = User.objects.get(id=video.user_id)
        tags = video.tags.split(",")  # l = ["","",""]
        if tags[-1] == "":
            tags.pop()
        ticks = time.process_time()
        if ticks > 6:
            video.views += 1
            video.save()
        rated = False
        user_reviews = video.review_set.all()
        for review in user_reviews:
            if request.user.username == review.user.username:
                rated = True
        reviews = video.review_set.order_by('-video_id')
        approves = []
        disapproves = []
        for review in reviews:
            approvedBy = review.approvedBy.split(',')
            approvedBy.pop()
            approves.append(len(approvedBy))
            disapprovedBy = review.disapprovedBy.split(',')
            disapprovedBy.pop()
            disapproves.append(len(disapprovedBy))
            rating = int(review.rating)
            review.rating = rating
        # sorting related
        lists = list(zip(reviews, approves, disapproves))
        rel_videos = []
        for v in videos:
            other_tags = v.tags.split(",")
            for tag in tags:
                if tag != " ":
                    for other in other_tags:
                        if other.lower() == tag.lower():
                            if v not in rel_videos and v != video:
                                rel_videos.append(v)
        rel_videos = rel_videos[-15:]
        rel_videos = sort_videos(rel_videos, 4, 10, 5)
        return render(request, 's_vid.html',
                      {'video': video, 'tags': tags, 'rated': rated, 'lists': lists, "rel_videos": rel_videos,
                       'users': users, 'user':user})
    elif request.method == 'POST':
        return render(request, 'home.html', {'users': users})
    else:
        return render(request, 'home.html', {'users': users})


# search for a video in db
def search_vid(request):
    users = User.objects.all()
    if request.method == 'POST':
        if (request.POST['search'] != "") and (request.POST['search'] is not None):
            channels = []
            term = request.POST['search']
            t = term.lower()
            videos = Video.objects.all()
            results = []
            hasRes = False
            for video in videos:
                title = video.title.lower()
                if t in title:
                    results.append(video)
            for channel in users:
                user = channel.username.lower()
                if t in user and (not (channel.is_superuser)):
                    channels.append(channel)

            if len(results) or len(channels) >= 1:
                hasRes = True
            else:
                hasRes = False

            for video in results:
                video.tags = video.tags.split(',')
                video.tags.pop()

            return render(request, 'search_res.html',
                          {'results': results, 'term': term, 'hasRes': hasRes, 'channels': channels, 'users': users})
        else:
            term = request.POST['search']
            hasRes = False
            return render(request, 'search_res.html', {'term': term, 'hasRes': hasRes, 'users': users})
    else:
        return render(request, 'home.html', {'users': users})


# update a video here (description and title only !):
def updt_vid(request, video_id):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        video = user.video_set.get(id=video_id)
        video_id = video.id
        form = UpdateVideoForm(instance=video)
        return render(request, 'updt_vid.html', {'form': form, 'video_id': video_id, 'users': users})
    elif request.method == 'POST' and request.user.is_authenticated:
        form = UpdateVideoForm(request.POST, request.FILES)
        user = request.user
        video = user.video_set.get(id=video_id)
        video_id = video.id
        if form.is_valid():
            t = form.cleaned_data['title']
            d = form.cleaned_data['description']
            tg = form.cleaned_data['tags']

            if video.title == t:
                pass
            else:
                if "TTS SUBS" == 1:
                    text = "Δοκιμή ήχου "
                    text_to_speech(text)
                old = video.title
                video.title = t
                for u in users:
                    if u != user:
                        if old in u.profile.notifications:
                            u.profile.notifications = u.profile.notifications.replace(old, t)
                            u.profile.save()
            if video.description == d:
                pass
            else:
                video.description = d

            if video.tags == tg:
                pass
            else:
                video.tags = tg
            video.save()
            return render(request, 'profile.html', {'users': users})
        else:
            return render(request, 'updt_vid.html', {'form': form, 'video_id': video_id, "users": users})
    else:
        return render(request, 'sign-in.html', {'users': users})


# deletes a specific video
def del_vid(request, video_id):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        video = user.video_set.get(id=video_id)
        for u in users:
            if video.title in u.profile.notifications:
                u.profile.notifications = u.profile.notifications.replace(video.title, " ")
                u.profile.count -= 1
                u.profile.save()
        video.delete()
        return render(request, 'profile.html', {'video': video, "users": users})
    else:
        return render(request, 'sign-in.html', {'users': users})


def del_notifications(request, notification_id):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        u = user.profile
        video = Video.objects.get(id=notification_id)
        if video.title in u.notifications:
            u.notifications = u.notifications.replace(video.title, " ")
            u.count -= 1
            u.save()
        return render(request, 'profile.html', {"u": u, 'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


def del_subscribes(request, channel_id):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        subscriber = request.user.profile
        channel_owner = User.objects.get(id=channel_id)

        if channel_owner.username in subscriber.subscribes:
            subscriber.subscribes = subscriber.subscribes.replace(channel_owner.username, " ")
            subscriber.save()

            # Update the channel owner's profile
            if subscriber.user.username in channel_owner.profile.subscribers:
                channel_owner.profile.subscribers = channel_owner.profile.subscribers.replace(subscriber.user.username,
                                                                                              " ")
                channel_owner.profile.save()

        return render(request, 'home.html', {'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


def toggle_subscription(request, channel_id):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        user = User.objects.get(id=channel_id)
        subscriber = request.user.profile

        if user.username in subscriber.subscribes:
            subscriber.subscribes = subscriber.subscribes.replace(user.username, " ")
            subscriber.save()

            if user.profile.subscribers and subscriber.user.username in user.profile.subscribers:
                user.profile.subscribers = user.profile.subscribers.replace(subscriber.user.username, " ")
                user.profile.save()

        else:
            subscriber.subscribes += " " + user.username
            subscriber.save()

            if subscriber.user.username not in user.profile.subscribers:
                user.profile.subscribers += " " + subscriber.user.username
                user.profile.save()
        return render(request, 'subscribe_button.html', {'user': user})
    else:
        return render(request, 'sign-in.html', {'users': users})

def view_vid(request):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        user = request.user
        videos = user.video_set.all()
        hasRes = False
        if len(videos) >= 1:
            hasRes = True
        else:
            hasRes = False
        return render(request, 'view_vid.html', {'hasRes': hasRes, 'videos': videos, 'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


# upload video to 'uploads/media/videos'
def upload_video(request):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        form = UploadVideoForm()
        return render(request, 'upload_video.html', {'form': form, 'users': users})
    elif request.method == 'POST' and request.user.is_authenticated:
        form = UploadVideoForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user
            print(user)
            print(user.profile)
            v = form.cleaned_data['video']
            t = form.cleaned_data['title']
            d = form.cleaned_data['description']
            tn = form.cleaned_data['thumbnail']
            tg = form.cleaned_data['tags']
            new_video = user.video_set.create(video=v, title=t, description=d, thumbnail=tn, tags=tg)
            new_video.save()
            if tn == "thumbnail/None/default_thumb.png":
                th = False
                s_vid = repr(new_video.video)
                s_vid = s_vid[19:]
                s_vid = s_vid[:-1]
                fileDir = os.path.dirname(os.path.realpath('__file__'))
                filename = os.path.join(fileDir, 'uploads/media/videos/' + s_vid)
                clip = VideoFileClip(filename).subclip(3, 4).to_ImageClip()
                # clip = VideoFileClip(filename).subclip(2,3).resize((256,144))
                # thumbnail = VideoFileClip('your_video.mp4').subclip(3, 4).resize((256, 144), resample='lanczos')
                # thumbnail.save_frame('thumbnail.jpg')
                # clip.save_frame((os.path.join(fileDir, 'uploads/media/thumbnails/' + s_vid)))
                s_vid = s_vid[:-4] + ".jpeg"
                clip.save_frame((os.path.join(fileDir, 'uploads/media/thumbnails/' + s_vid)))
                new_video.thumbnail = 'thumbnails/' + s_vid
                new_video.save()
            else:
                th = True
            for u in users:
                if u != user and (user.username in u.profile.subscribes):
                    u = u.profile
                    u.notifications = u.notifications + " " + t
                    u.count += 1
                    u.save()
            return render(request, 'profile.html', {"users": users, "th": th})
        else:
            return render(request, 'upload_video.html', {'form': form, 'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


# reset your password
def reset_pwd(request):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        form = ResetPasswordForm()
        return render(request, 'reset_pwd.html', {'form': form, 'users': users})
    elif request.method == 'POST' and request.user.is_authenticated:
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_pwd = form.cleaned_data["password"]
            uname = request.user.username
            user = User.objects.get(username=uname)
            user.set_password(new_pwd)
            user.save()
            return render(request, 'profile.html', {'users': users})
        else:
            return render(request, 'reset_pwd.html', {'form': form, 'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


def notifications(request):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        u = request.user
        videos = Video.objects.all()
        not_vid = []
        nots = []
        notif = u.profile.notifications
        for v in videos:
            if (v.title in notif) and (notif != ""):
                if v.title not in nots:
                    nots.append(v.title)
                    not_vid.append(v)
        hasRes = False
        if len(not_vid) >= 1:
            hasRes = True
        else:
            hasRes = False
        return render(request, 'notifications.html',
                      {'hasRes': hasRes, "nots": nots, "not_vid": not_vid, 'users': users})
    else:
        return render(request, 'home.html', {'users': users})


def sub(request, channel_id):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        subscriber = request.user.profile
        channel_owner = User.objects.get(id=channel_id)
        # channel_owner = User.objects.get(id=channel_id)
        if channel_owner.username not in subscriber.subscribes:
            subscriber.subscribes = subscriber.subscribes + " " + channel_owner.username
            subscriber.save()

        # Update the subscribers field of the channel owner's profile
        if subscriber.user.username not in channel_owner.profile.subscribers:
            channel_owner.profile.subscribers += " " + subscriber.user.username
            channel_owner.profile.save()
        return render(request, 'home.html', {'users': users})
    else:
        return render(request, 'home.html', {'users': users})


def subscribes(request):
    users = User.objects.all()
    if request.user.is_authenticated:
        u = request.user
        videos = Video.objects.all()
        sub_vid = []
        subscr = []
        subchan = []
        subs = u.profile.subscribes
        for v in videos:
            if (v.user.username in subs) and (subs != ""):
                if v.user not in subchan and v.user != u:
                    subscr.append(v.user.username)
                    subchan.append(v.user)
                    sub_vid.append(v)
        hasRes = False
        if len(sub_vid) >= 1:
            hasRes = True
        else:
            hasRes = False
        return render(request, 'subscribes.html',
                      {'hasRes': hasRes, "subscr": subscr, "sub_vid": sub_vid, "subchan": subchan, 'users': users})
    else:
        return render(request, 'home.html', {'users': users})


# edit profile picture
def edit_avatar(request):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        form = EditAvatarForm()
        return render(request, 'edit_avatar.html', {'form': form, 'users': users})
    elif request.method == 'POST' and request.user.is_authenticated:
        form = EditAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            def_img = "avatar/None/default_avatar.png"
            new_image = form.cleaned_data["image"]
            if def_img == new_image:
                error = "You haven't selected any image. Please try again."
                return render(request, 'profile.html', {'form': form, 'error': error, 'users': users})
            else:
                profile = request.user.profile
                profile.image = new_image
                profile.save()
                return render(request, 'profile.html', {})
        else:
            return render(request, 'edit_avatar.html', {'form': form, 'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


# view your profile
def profile(request):
    users = User.objects.all()
    if request.method == 'GET' and request.user.is_authenticated:
        return render(request, 'profile.html', {'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


# Signs in the user
def signin_view(request):
    users = User.objects.all()
    if request.method == 'GET':
        if request.user.is_authenticated:
            return render(request, 'profile.html', {'users': users})
        else:
            return render(request, 'sign-in.html', {'users': users})
    elif request.method == 'POST':
        uname = request.POST['uname']
        pwd = request.POST['pwd']
        user = authenticate(username=uname, password=pwd)

        if user is not None:
            login(request, user)
            return render(request, 'profile.html', {'users': users})
        else:
            error = 'Username or password are invalid. Please, try again.'
            return render(request, 'sign-in.html', {'error': error, 'users': users})
    else:
        return render(request, 'sign-in.html', {'users': users})


# Signs up the user
def signup_view(request):
    users = User.objects.all()
    if request.method == 'POST':
        if request.user.is_authenticated:
            return render(request, 'profile.html', {'users': users})

        form = UserRegFrom(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            uname = form.cleaned_data["username"]
            user = form.save(commit=False)
            pwd = form.cleaned_data["password"]
            user.set_password(pwd)
            user.save()
            user = authenticate(username=uname, password=pwd)
            login(request, user)
            profile = Profile(user_id=user.id)
            profile.save()
            img_path = user.profile.image
            print("Image math: ", img_path)

            return render(request, 'profile.html', {'users': users})

        else:
            return render(request, 'sign-up.html', {'form': form, 'users': users})
    else:
        if (request.method == 'GET') and (not request.user.is_authenticated):
            form = UserRegFrom()
            return render(request, 'sign-up.html', {'form': form, 'users': users})
        else:
            return render(request, 'home.html', {'users': users})


# Logs out the user
def signout_view(request):
    users = User.objects.all()
    logout(request)
    return render(request, 'sign-in.html', {'users': users})
