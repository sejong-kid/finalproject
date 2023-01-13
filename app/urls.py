from django.urls import path, include
from . import views
urlpatterns = [
    path('home/', views.home),
    path('search/', views.search),
    path('article/', views.article),

    path('upload/', views.upload),
    path('read/', views.read)

]
