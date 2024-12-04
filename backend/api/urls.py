from django.urls import path, include
from . import views
urlpatterns = [
    path('home/', views.HomeView.as_view()),
    path('html/', views.html)
]


