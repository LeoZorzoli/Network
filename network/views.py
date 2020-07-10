from django import forms
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Profile, Like

class Edit(forms.Form):
    textarea = forms.CharField(widget=forms.Textarea(attrs={'rows': 1,
                              'cols': 152, 'rows':10}), label='')


def index(request):

    posts = Post.objects.all().order_by('id').reverse()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {'page_obj': page_obj})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    if request.method == 'GET':
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(user=profileuser).order_by('id').reverse()
        follower = Profile.objects.filter(target=profileuser)
        following = Profile.objects.filter(follower=profileuser)
        if request.user.is_anonymous:
            return redirect('login')
        else:
            following_each_other = Profile.objects.filter(follower=currentuser, target=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)
            paginator = Paginator(posts, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            return render(request, "network/profile.html", {'profileuser': profileuser,
            'page_obj': page_obj, 'follower':totalfollower, 'following': totalfollowing,
            'followingEachOther': following_each_other})
        
    else:
        currentuser = request.user
        profileuser = get_object_or_404(User, username=username)
        posts = Post.objects.filter(user=profileuser).order_by('id').reverse()
        following_each_other = Profile.objects.filter(follower=request.user, target=profileuser)
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        if not following_each_other:
            follow = Profile.objects.create(target=profileuser, follower=currentuser)
            follow.save()
            follower = Profile.objects.filter(target=profileuser)
            following = Profile.objects.filter(follower=profileuser)
            following_each_other = Profile.objects.filter(follower=request.user, target=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)

            return render(request, "network/profile.html", {'profileuser': profileuser, 
            'page_obj': page_obj, 'follower': totalfollower, 'following': totalfollowing,
            'followingEachOther': following_each_other})

        else:
            following_each_other.delete()
            follower = Profile.objects.filter(target=profileuser)
            following = Profile.objects.filter(follower=profileuser)
            totalfollower = len(follower)
            totalfollowing = len(following)
       
            return render(request, "network/profile.html", {'profileuser': profileuser, 
            'page_obj': page_obj, 'follower': totalfollower, 'following': totalfollowing,
            'followingEachOther': following_each_other})


def newpost(request, username):
    if request.method == 'GET':
        user = get_object_or_404(User, username=username)
        return render(request, "network/newpost.html", {'user':user})
    else:
        user = get_object_or_404(User, username=username)
        textarea = request.POST["textarea"]
        post = Post.objects.create(content=textarea, user=user)
        post.save()
        return redirect("index")


def following(request, username):
    if request.method == 'GET':
        currentuser = get_object_or_404(User, username=username)
        follows = Profile.objects.filter(follower=currentuser)
        posts = Post.objects.all().order_by('id').reverse()
        posted = []
        for p in posts:
            for follower in follows:
                if follower.target == p.user:
                    posted.append(p)
        
        if not follows:
            return render(request, 'network/following.html', {'message': "You don't follow anybody"})

        paginator = Paginator(posted, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'network/following.html', {'page_obj':page_obj})


def edit(request, post_id):
    if request.method == 'GET':
        post = Post.objects.get(pk=post_id)
        return render(request, 'network/edit.html', {'post_id': post_id, 'edit': Edit(initial={'textarea': post.content})})
    else:
        post = Post.objects.get(pk=post_id)
        form = Edit(request.POST) 
        if form.is_valid():
            textarea = form.cleaned_data["textarea"]
            post.content = textarea
            post.save()
            return redirect('index')



def like_post(request):
    user = request.user
    if request.method == 'GET':
        post_id = request.GET['post_id']
        likedpost = Post.objects.get(pk=post_id)
        if user in likedpost.liked.all():
            likedpost.liked.remove(user)
            like = Like.objects.get(post=likedpost, user=user)
            like.delete()
        else:
            like = Like.objects.get_or_create(post=likedpost, user=user)
            likedpost.liked.add(user)
            likedpost.save()
        
        return HttpResponse('Success')
    