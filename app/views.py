from django.contrib.auth import login, authenticate
from django.shortcuts import render, HttpResponseRedirect, redirect, get_object_or_404
from django.http  import HttpResponse
import datetime as dt
from django.http import HttpResponse, Http404,HttpResponseRedirect
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_logout
from django.conf import settings 
from django.core.mail import send_mail 
from django.urls import reverse
from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('/')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

# def signin(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(username=username, password=password)
#     if user is not None:
#         login(request, user)
#         return redirect(request,'/')
    
#     return render(request, 'registration/login.html')

@login_required
def logout(request):
    django_logout(request)
    return  HttpResponseRedirect('/')

class UserProfiles(APIView):
    def get(self, request, format=None):
        profile = Profile.objects.all().order_by('id')
        serializers = ProfileSerializer(profile, many=True)
        return Response(serializers.data)
    
class Projects(APIView):
    def get(self, request, format=None):
        project = Project.objects.all().order_by('-date')
        serializers = ProjectSerializer(project, many=True)
        return Response(serializers.data)

def index(request):
    post = Project.objects.all()
    first = Project.objects.order_by('?').first()
    form = RatingForm(request.POST)
            
    return render(request, 'index.html', {'post':post[::-1], 'first':first, 'form':form})
    

@login_required
def single_project(request,post_id):
    post = get_object_or_404(Project, id=post_id)
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    comments = Comment.objects.filter(project=post).order_by('-date')
    ratings = Rating.objects.filter(user=request.user, post=post).first()
    rating_status = None
    if ratings is None:
        rating_status = False
    else:
        rating_status = True
    if request.method == 'POST':
        form_r= RatingForm(request.POST)
        if form_r.is_valid():
            rate = form_r.save(commit=False)
            rate.user = request.user
            rate.post = post
            rate.save()
            post_ratings = Rating.objects.filter(post=post)

            design_ratings = [d.design for d in post_ratings]
            design_average = sum(design_ratings) / len(design_ratings)

            usability_ratings = [us.usability for us in post_ratings]
            usability_average = sum(usability_ratings) / len(usability_ratings)

            content_ratings = [content.content for content in post_ratings]
            content_average = sum(content_ratings) / len(content_ratings)

            score = (design_average + usability_average + content_average) / 3
            print(score)
            rate.design_average = round(design_average, 2)
            rate.usability_average = round(usability_average, 2)
            rate.content_average = round(content_average, 2)
            rate.score = round(score, 2)
            rate.save()
            return HttpResponseRedirect(request.path_info)
    else:
        form_r = RatingForm()
                
    
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = request.POST.get("comment")
            user = request.user
            project = post
            get_comment = Comment(comment=comment, project=project,profile=profile)
            get_comment.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            form = CommentForm()
    
    return render(request, 'awards.html', {'post':post, 'form':CommentForm, 'comments':comments,'profile':profile, 'rating_form':form_r,'rating':ratings,}) 
@login_required
def like(request,post_id):
    user = request.user
    post = Project.objects.get(id=post_id)
    current_likes = post.like
    
    liked = Likes.objects.filter(user=user, project=post).count()
    
    if not liked:
        like = Likes.objects.create(user=user,project=post)
        
        current_likes = current_likes + 1
        
    else:
        Likes.objects.filter(user=user,project=post).delete()
        current_likes = current_likes - 1
        
    post.like = current_likes
    post.save() 
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))  

@login_required
def profile_edit(request,username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    form = EditProfileForm(instance=profile)
    
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = user
            data.save()
            return HttpResponseRedirect(reverse('profile', args=[username]))
        else:
            form = EditProfileForm(instance=profile)
    legend = 'Edit Profile'
    return render(request, 'profile/update.html', {'legend':legend, 'form':EditProfileForm})

    
@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    posts = Project.objects.filter(user=user).order_by("-date")
    
    post_count = Project.objects.filter(user=user).count()

    
    return render(request,'profile/profile.html', {'user':user, 'profile':profile, 'posts':posts, 'post_count':post_count})

@login_required
def post_project(request):
    userX = request.user
    user = Profile.objects.get(user=request.user)
    
    if request.method == "POST":
        
        form = ProjectForm(request.POST, request.FILES)
        
        if form.is_valid():
            data = form.save(commit=False)
            data.profile = user
            data.user = userX
            data.save()
            return redirect('/')
        else:
            return False
    
    return render(request, 'new_post.html', {'form':ProjectForm})


def search_results(request):
    
    if "project" in request.GET and request.GET["project"]:
        search_term = request.GET.get("project")
        searched_projects = Project.search_projects(search_term)
        message = f"{search_term}"

        return render(request, 'search.html',{"message":message, "post":searched_projects})

    else:
        message = "You haven't searched for any project"
        return render(request, 'search.html',{"message":message})

# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             user.refresh_from_db()  # load the profile instance created by the signal
#             user.profile.job_title = form.cleaned_data.get('job_title')
#             user.save()
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=user.username, password=raw_password)
#             login(request, user)
#             return redirect('/')
#     else:
#         form = SignUpForm()
#     return render(request, 'signup.html', {'form': form})