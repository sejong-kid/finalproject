from django.urls import path
from . import views
urlpatterns = [
    # path('upload/', views.upload),
    # path('upload_inverse/', views.upload_inverse),
    path('index/', views.index),
    path('',views.index),
    path('read_json/',views.read_json),
    path('search/',views.search),
    path('add_word/',views.add_word),
]
