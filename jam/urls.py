from django.urls import path

from jam import views

app_name = 'jam'

from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.contest.Index.as_view(), name='index'),

    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('signup', views.SignupView.as_view(), name='signup'),

    path('p/new', views.ProblemCreate.as_view(), name='problem-create'),
    path('p/<slug>', views.ProblemDetail.as_view(), name='problem'),
    path('p/<slug>/delete', views.ProblemDelete.as_view(), name='problem-delete'),
]
