from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('', views.index, name='MainPage'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('search/', views.search_results, name='search'),
    path('logout/', views.logout, name='logout'),
    path('account/', include('django.contrib.auth.urls')),
    path('add_new_project/', views.post_project, name='addProject'),
    path('<uuid:post_id>', views.single_project, name='singleProject'),
    path('<uuid:post_id>/like', views.like, name='likePost'),
    path('profile/<username>', views.profile, name='profile'),
    path('profile/<username>/edit', views.profile_edit, name='editProfile'),
    path('api/user_profiles', views.UserProfiles.as_view()),
    path('api/projects', views.Projects.as_view()),
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)