from django.urls import path

from jam import views

app_name = 'jam'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('p/list', views.ProblemList.as_view(), name='problem-list'),
    path('p/new', views.ProblemCreate.as_view(), name='problem-create'),
    path('p/<slug>', views.ProblemDetail.as_view(), name='problem'),
]
