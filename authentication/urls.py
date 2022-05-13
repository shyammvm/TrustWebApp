from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('upload', views.upload, name='upload'),
    path('index', views.index, name='index'),
    path('search', views.search, name='search'),
    path('<int:pk>/profile', views.ProfileView.as_view(), name='profile'),
    path('links', views.links, name='links'),
    path('verify', views.verify, name='verify'),
    path('verification', views.verification, name='verification'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
