from django.db import models
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
import uuid

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.profile.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    location = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(max_length=120, null=True)
    avatar = CloudinaryField('image')
    
    def __str__(self):
        return self.user.username
    
    def save_image(self):
        self.save()
        
    def delete_image(self):
        self.delete()
        
    def get_projects(self, username):
        user = get_object_or_404(User, username=username)
        return Project.objects.filter(user=user).count()
    
    @classmethod
    def update(cls, id, value):
        cls.objects.filter(id=id).update(avatar=value)
        
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

    
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_user')
    image = CloudinaryField('image')
    project_name = models.CharField(max_length=120, null=True)
    description = models.TextField(max_length=1000, verbose_name='project Description', null=True)
    date = models.DateTimeField(auto_now_add=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='post_profile')
    like = models.IntegerField(default=0)

    
    def __str__(self):
        return self.project_name
    
    def save_image(self):
        self.save()
        
    @classmethod
    def search_projects(cls,search_term):
        posts = Project.objects.filter(project_name__icontains=search_term)
        return posts
        
    def delete_image(self):
        self.delete()  
        
    def no_of_rating(self):
        ratings = Rating.objects.filter(project=self)
        return len(ratings)
    
    def ave_des(self):
        rate = Rating.objects.filter(post=self)
        ret = rate.aggregate(Avg('design'))
        design = ret['design__avg']
        return design
    
    def ave_use(self):
        rate = Rating.objects.filter(post=self)
        ret = rate.aggregate(Avg('usability'))
        usability = ret['usability__avg']
        return usability
    
    def ave_cont(self):
        rate = Rating.objects.filter(post=self)
        ret = rate.aggregate(Avg('content')) 
        content = ret['content__avg']
        return content
    
    def all_ave(self):
        total = 0
        a = Rating.objects.filter(post=self)
        ave = [a.aggregate(Avg('design'))['design__avg'], a.aggregate(Avg('usability'))['usability__avg'], a.aggregate(Avg('content'))['content__avg']]
        
        for items in ave:
            total = total + items
                    
        return total / len(ave)
            
        
    
    # def average_ratings(self):
    #     sum = 0
    #     ratings = Rating.objects.filter(project=self)
        
    #     for rating in ratings:
    #         sum += rating.design + rating.usability + rating.content
    #         return sum
            
    #     # if len(ratings) > 0 :
    #     #     return sum / len(ratings)
        
    #     # else:
    #     #     return 0        
        
class Rating(models.Model):
    rating = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )

    design = models.IntegerField(choices=rating, default=0, blank=True)
    usability = models.IntegerField(choices=rating, blank=True)
    content = models.IntegerField(choices=rating, blank=True)
    score = models.FloatField(default=0, blank=True)
    design_average = models.FloatField(default=0, blank=True)
    usability_average = models.FloatField(default=0, blank=True)
    content_average = models.FloatField(default=0, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='rater')
    post = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings', null=True)

    def save_rating(self):
        self.save()

    @classmethod
    def get_ratings(cls, id):
        ratings = Rating.objects.filter(post_id=id).all()
        return ratings

    def __str__(self):
        return f'{self.post} Rating'
            
    
class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateTimeField()
    
    def add_project(sender,instance,*args,**kwargs):
        project = instance
        user = project.user

            
class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='post_like')

class Comment(models.Model):
    comment = models.TextField(null=True)
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment')
    date = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='post_comment')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='commenter_profile')
            
post_save.connect(Stream.add_project, sender=Project)