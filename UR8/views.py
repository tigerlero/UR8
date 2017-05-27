# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from .forms import UserRegFrom, EditAvatarForm, ResetPasswordForm, UploadVideoForm, UpdateVideoForm
from .models import Profile, Video, Review
from django.contrib.auth.models import User
from django.http import HttpResponse
# from moviepy.editor import *
from math import floor, ceil, modf
import json
import time

# def thumb(id):
#     video = Video.objects.get(id=id)
#     print(video)
#     v = ""
#
#     clip = VideoFileClip(video)
#     clip.save_frame("thumbnail.jpg", t=0.00)
#     return clip
#
#
# def generate_thumbnails(tmp_directory):
#     clip = VideoFileClip(os.path.join(tmp_directory, "video.mp4"))
#     for i in range(3):
#         thumbnail = os.path.join(tmp_directory, "thumbnail_%s.png" % i)
#         clip.save_frame(thumbnail, t=random.uniform(0.1, clip.duration))

# Create your views here.
# Login is required to view this page..
def home(request):
    if request.method == 'GET':
        videos = Video.objects.all()
        video_results = []
        new = []
        popular = []
        best = []
        users = User.objects.all()
        for video in videos:
            video_results.append(video)
            new.append(video)
            popular.append(video)
            best.append(video)
        video_results = video_results[-19:]
        new = new[-19:]
        popular = popular[-19:]
        best = best[-19:]
        video_results = sort_videos(video_results)
        new = new_videos(new)
        popular = popular_videos(popular)
        best = best_videos(best)
        hasRes = False
        if len(video_results) >= 1:
            hasRes = True
        else:
            hasRes = False
        # for video in video_results:
        #     video.tags = video.tags.split(',')
        #     video.tags.pop()

        return render(request, 'home.html', {'video_results': video_results, 'hasRes': hasRes, 'users': users, 'new': new, 'popular': popular, 'best': best})


def sort_videos(videos):
    overall = [0]*30
    # calculate overall score
    for i, video in enumerate(videos):
        overall[i] += 5 * video.id
        overall[i] += 10 * video.avg_rating
        overall[i] += 7 * video.views
    # insertion sort for overall score
    for i in range(1, len(videos)):
        j = i
        while (j > 0) and (overall[j] > overall[j - 1]):
            videos[j], videos[j - 1] = videos[j - 1], videos[j]
            overall[j], overall[j - 1] = overall[j - 1], overall[j]
            j -= 1
    return videos


def best_videos(videos):
    overall = [0]*30
    # calculate overall score
    for i, video in enumerate(videos):
        overall[i] += 1 * video.id
        overall[i] += 10 * video.avg_rating
        overall[i] += 1 * video.views
    # insertion sort for overall score
    for i in range(1, len(videos)):
        j = i
        while (j > 0) and (overall[j] > overall[j - 1]):
            videos[j], videos[j - 1] = videos[j - 1], videos[j]
            overall[j], overall[j - 1] = overall[j - 1], overall[j]
            j -= 1
    return videos


def popular_videos(videos):
    overall = [0]*30
    # calculate overall score
    for i, video in enumerate(videos):
        overall[i] += 1 * video.id
        overall[i] += 1 * video.avg_rating
        overall[i] += 10 * video.views
    # insertion sort for overall score
    for i in range(1, len(videos)):
        j = i
        while (j > 0) and (overall[j] > overall[j - 1]):
            videos[j], videos[j - 1] = videos[j - 1], videos[j]
            overall[j], overall[j - 1] = overall[j - 1], overall[j]
            j -= 1
    return videos


def new_videos(videos):
    overall = [0]*30
    # calculate overall score
    for i, video in enumerate(videos):
        overall[i] += 10 * video.id
        overall[i] += 1 * video.avg_rating
        overall[i] += 1 * video.views
    # insertion sort for overall score
    for i in range(1, len(videos)):
        j = i
        while (j > 0) and (overall[j] > overall[j - 1]):
            videos[j], videos[j - 1] = videos[j - 1], videos[j]
            overall[j], overall[j - 1] = overall[j - 1], overall[j]
            j -= 1
    return videos


def channel(request, username):
    if request.method == 'GET':
        user = User.objects.get(username=username)
        videos = user.video_set.all()
        hasRes = False
        if len(videos) >= 1:
            hasRes = True
        else:
            hasRes = False

        for video in videos:
            video.tags = video.tags.split(',')
            video.tags.pop()

        return render(request, 'channel.html', {'hasRes': hasRes, 'videos': videos, 'user': user})
    else:
        return render(request, 'home.html', {})


def channels(request):
    if request.method == 'GET':
        users = User.objects.all()
        return render(request, 'channels.html', {'users': users})
    else:
        return render(request, 'home.html', {})


def edit_review(request, vid, rid):
    if request.method == 'GET' and request.user.is_authenticated():
        review = Review.objects.get(id=rid)
        video = video = Video.objects.get(id=vid)
        vID = video.id
        return render(request, 'edit_review.html', {'review':review, 'vID':vID})
    elif request.method == 'POST' and request.is_ajax() and request.POST['edit_review'] == 'yes' and request.user.is_authenticated():

        newText = request.POST['text']
        newVal = int(request.POST['rating']) # new rating
        video = video = Video.objects.get(id=vid)
        review = Review.objects.get(id=rid)

        # remove old rating
        old_avg = float(video.avg_rating)
        rating = float(review.rating)
        count = float(video.rating_counter)
        new_avg = 0.0
        if (count - 1) > 0:
            new_avg = ( (old_avg * count) - rating ) / ( count-1 )

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
        video.avg_rating = (old_avg2 * (count2-1) + newVal)/count2
        video.save()

        data = {'ok': 'yes'}
        return HttpResponse(json.dumps(data), content_type='application/json')


def delete_review(request, rID):
    if request.method == 'POST' and request.is_ajax() and request.POST['del_review'] == 'yes' and request.user.is_authenticated():
        review = Review.objects.get(id=rID)
        vID = request.POST['vID']
        video = Video.objects.get(id=vID)

        # average = ((average * nbValues) - value) / (nbValues - 1)
        old_avg = float(video.avg_rating)
        rating = float(review.rating)
        count = float(video.rating_counter)
        new_avg = 0.0
        if (count - 1) > 0:
            new_avg = ( (old_avg * count) - rating ) / ( count-1 )

        video.avg_rating = new_avg
        video.rating_counter -= 1
        video.save()

        review.delete()
        data = {'ok':'yes'}
        return HttpResponse(json.dumps(data), content_type='application/json')


def rated_review2(request, vID, rID):
    if request.method == 'POST' and request.is_ajax() and (request.POST['disapprove'] == 'yes'):
        video = Video.objects.get(id=vID)
        review = Review.objects.get(id=rID)
        uname = request.user.username

        if request.POST['disapprove'] == 'yes':
            if (uname in review.disapprovedBy):
                data = {'ok':'yes'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                if uname in review.approvedBy:
                    review.disapprovedBy += uname
                    review.disapprovedBy += ","
                    liked = review.approvedBy.replace(''+uname+',', "")
                    review.approvedBy = liked
                    review.save()

                    data = {'ok':'yes'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    review.disapprovedBy += uname
                    review.disapprovedBy += ","
                    review.save()

                    data = {'ok':'yes'}
                    return HttpResponse(json.dumps(data), content_type='application/json')


def rated_review(request, vID, rID):
    if request.method == 'POST' and request.is_ajax() and (request.POST['approve'] == 'yes'):
        video = Video.objects.get(id=vID)
        review = Review.objects.get(id=rID)
        uname = request.user.username

        if request.POST['approve'] == 'yes':
            if (uname in review.approvedBy):
                data = {'ok':'yes'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                if uname in review.disapprovedBy:
                    review.approvedBy += uname
                    review.approvedBy += ","
                    disliked = review.disapprovedBy.replace(''+uname+',', "")
                    review.disapprovedBy = disliked
                    review.save()

                    data = {'ok':'yes'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    review.approvedBy += uname
                    review.approvedBy += ","
                    review.save()
                    data = {'ok':'yes'}
                    return HttpResponse(json.dumps(data), content_type='application/json')


def rated_video(request, id):
    if request.method == 'POST' and request.is_ajax() and request.POST['rated'] == 'yes':
        video = Video.objects.get(id=id)
        text = request.POST['text']
        rating = int(request.POST['rating'])
        review = Review(user=request.user, video=video, text=text, rating=rating)
        review.save()
        video.rating_counter += 1
        # (previous_mean * (count -1)) + new_value) / count
        old_avg = video.avg_rating
        count = video.rating_counter
        video.avg_rating = (old_avg * (count-1) + rating)/count
        video.save()
        data = {'ok':'yes'}
        return HttpResponse(json.dumps(data), content_type='application/json')


# view a specific uploaded video
def s_vid(request, id):
    if request.method == 'GET':
        video = Video.objects.get(id=id)
        videos = Video.objects.all()
        tags = video.tags.split(",")  # l = ["","",""]
        if tags[-1] == "":
            tags.pop()
        ticks = time.clock()
        if ticks > 6:
            video.views += 1
            video.save()
        rated = False
        user_reviews = video.review_set.all()
        for review in user_reviews:
            if request.user.username == review.user.username:
                rated = True

        reviews = video.review_set.order_by('-pk')
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
                for other in other_tags:
                    if other.lower() == tag.lower():
                        if v not in rel_videos and v != video:
                            rel_videos.append(v)

        rel_videos = rel_videos[-5:]
        rel_videos = sort_videos(rel_videos)
        return render(request, 's_vid.html', {'video': video, 'tags': tags, 'rated': rated, 'lists': lists, "rel_videos":rel_videos})
    elif request.method == 'POST':
        return render(request, 'home.html', {})
    else:
        return render(request, 'home.html', {})


# search for a video in db
def search_vid(request):
    if request.method == 'POST':
        if (request.POST['search'] != "") and (request.POST['search'] is not None):
            users = User.objects.all()
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

            return render(request, 'search_res.html', {'results': results, 'term': term, 'hasRes': hasRes, 'channels': channels})
        else:
            term = request.POST['search']
            hasRes = False
            return render(request, 'search_res.html', {'term': term, 'hasRes': hasRes})
    else:
        return render(request, 'home.html', {})


# update a video here (description and title only !):
def updt_vid(request, id):
    if request.method == 'GET' and request.user.is_authenticated():
        user = request.user
        video = user.video_set.get(id=id)
        pk = video.id
        form = UpdateVideoForm(instance=video)
        return render(request, 'updt_vid.html', {'form': form, 'pk': pk})
    elif request.method == 'POST' and request.user.is_authenticated():
        form = UpdateVideoForm(request.POST, request.FILES)
        user = request.user
        video = user.video_set.get(id=id)
        pk = video.id
        users = User.objects.all()
        if form.is_valid():
            t = form.cleaned_data['title']
            d = form.cleaned_data['description']
            tg = form.cleaned_data['tags']

            if video.title == t:
                pass
            else:
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
            return render(request, 'profile.html', {})
        else:
            return render(request, 'updt_vid.html', {'form': form, 'pk': pk,"users":users})
    else:
        return render(request, 'sign-in.html', {})


# deletes a specific video
def del_vid(request, id):
    if request.method == 'GET' and request.user.is_authenticated():
        user = request.user
        users = User.objects.all()
        video = user.video_set.get(id=id)

        for u in users:
                if video.title in u.profile.notifications:
                    u.profile.notifications = u.profile.notifications.replace(video.title, " ")
                    u.profile.count -= 1
                    u.profile.save()
        video.delete()
        return render(request, 'profile.html', {'video': video, "users": users})
    else:
        return render(request, 'sign-in.html', {})


def del_notifications(request, id):
    if request.method == 'GET' and request.user.is_authenticated():
        user = request.user
        u = user.profile
        video = Video.objects.get(id=id)
        if video.title in u.notifications:
            u.notifications = u.notifications.replace(video.title, " ")
            u.count -= 1
            u.save()
        return render(request, 'profile.html', {"u": u})
    else:
        return render(request, 'sign-in.html', {})


def del_subscribes(request, id):
    if request.method == 'GET' and request.user.is_authenticated():
        u = request.user.profile
        video = Video.objects.get(id=id)
        if video.user.username in u.subscribes:
            u.subscribes = u.subscribes.replace(video.user.username, " ")
            u.save()
        return render(request, 'profile.html', {"u": u, "video": video})
    else:
        return render(request, 'sign-in.html', {})


def view_vid(request):
    if request.method == 'GET' and request.user.is_authenticated():
        user = request.user
        videos = user.video_set.all()
        hasRes = False
        if len(videos) >= 1:
            hasRes = True
        else:
            hasRes = False

        return render(request, 'view_vid.html', {'hasRes': hasRes, 'videos': videos})
    else:
        return render(request, 'sign-in.html', {})


# upload video to 'uploads/media/videos'
def upld_vid(request):
    if request.method == 'GET' and request.user.is_authenticated():
        form = UploadVideoForm()
        return render(request, 'upld_vid.html', {'form': form})
    elif request.method == 'POST' and request.user.is_authenticated():
        form = UploadVideoForm(request.POST, request.FILES)
        if form.is_valid():
            users = User.objects.all()
            user = request.user
            v = form.cleaned_data['video']
            t = form.cleaned_data['title']
            d = form.cleaned_data['description']
            tn = form.cleaned_data['thumpnail']
            tg = form.cleaned_data['tags']
            new_video = user.video_set.create(video=v, title=t, description=d, thumpnail=tn, tags=tg)
            new_video.save()
            # videos = Video.objects.all()
            # for video in videos:
            #     if video.thumpnail == "thumpnail/None/default_thump.png":
            #         im = thumb(video.id)
            #         print(im)
            #         video.thumpnail = im
            #         video.save()

            for u in users:
                if u != user and (user.username in u.profile.subscribes):
                    u = u.profile
                    u.notifications = u.notifications + " " + t
                    u.count += 1
                    u.save()
            return render(request, 'profile.html', {"users": users})
        else:
            return render(request, 'upld_vid.html', {'form': form})
    else:
        return render(request, 'sign-in.html', {})


# reset your password
def reset_pwd(request):
    if request.method == 'GET' and request.user.is_authenticated():
        form = ResetPasswordForm()
        return render(request, 'reset_pwd.html', {'form': form})
    elif request.method == 'POST' and request.user.is_authenticated():
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_pwd = form.cleaned_data["password"]
            uname = request.user.username
            user = User.objects.get(username=uname)
            user.set_password(new_pwd)
            user.save()
            return render(request, 'profile.html', {})
        else:
            return render(request, 'reset_pwd.html', {'form': form})
    else:
        return render(request, 'sign-in.html', {})


def notifications(request):
    if request.method == 'GET' and request.user.is_authenticated():
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
        return render(request, 'notifications.html', {'hasRes': hasRes, "nots": nots, "not_vid": not_vid})
    else:
        return render(request, 'home.html', {})


def sub(request, id):
    if request.method == 'GET' and request.user.is_authenticated():
        # subscribe
        u = request.user.profile
        video = Video.objects.get(id=id)
        if video.user.username not in u.subscribes:
            u.subscribes = u.subscribes + " " + video.user.username
            u.save()
        return render(request, 'profile.html', {"video": video})
    else:
        return render(request, 'home.html', {})


def subscribes(request):
    if request.user.is_authenticated():
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
        return render(request, 'subscribes.html', {'hasRes': hasRes, "subscr": subscr, "sub_vid": sub_vid, "subchan": subchan})
    else:
        return render(request, 'home.html', {})

# edit profile picture
def edit_avatar(request):
    if request.method == 'GET' and request.user.is_authenticated():
        form = EditAvatarForm()
        return render(request, 'edit_avatar.html', {'form': form})
    elif request.method == 'POST' and request.user.is_authenticated():
        form = EditAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            def_img = "avatar/None/default_avatar.png"
            new_image = form.cleaned_data["image"]
            if def_img == new_image:
                error = "You haven't selected any image. Please try again."
                return render(request, 'profile.html', {'form': form, 'error': error})
            else:
                profile = request.user.profile
                profile.image = new_image
                profile.save()
                return render(request, 'profile.html', {})
        else:
            return render(request, 'edit_avatar.html', {'form': form})
    else:
        return render(request, 'sign-in.html', {})


# view your profile
def profile(request):
    if request.method == 'GET' and request.user.is_authenticated():
        return render(request, 'profile.html', {})
    else:
        return render(request, 'sign-in.html', {})


# Signs in the user..
def signin_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated():
            return render(request, 'profile.html', {})
        else:
            return render(request, 'sign-in.html', {})
    elif request.method == 'POST':
        uname = request.POST['uname']
        pwd = request.POST['pwd']
        user = authenticate(username=uname, password=pwd)

        if user is not None:
            login(request, user)
            return render(request, 'profile.html', {})
        else:
            error = 'Username or password are invalid. Please, try again.'
            return render(request, 'sign-in.html', {'error': error})
    else:
        return render(request, 'sign-in.html', {})


# Signs up the user..
def signup_view(request):
    if request.method == 'POST':

        if request.user.is_authenticated():
            return render(request, 'profile.html', {})

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

            return render(request, 'profile.html', {})

        else:
            return render(request, 'sign-up.html', {'form': form})
    else:
        if (request.method == 'GET') and (not request.user.is_authenticated()):
            form = UserRegFrom()
            return render(request, 'sign-up.html', {'form': form})
        else:
            return render(request, 'home.html', {})


# Logs out the user..
def signout_view(request):
    logout(request)
    return render(request, 'sign-in.html', {})
