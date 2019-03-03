from django.urls import path

from jam import views

app_name = 'jam'

urlpatterns = [
    path('', views.Index.as_view()),
]
