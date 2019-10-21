from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from contest import views

app_name = 'contest'

urlpatterns = [
    path('', views.contest.Index.as_view(), name='index'),

    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('signup', views.SignupView.as_view(), name='signup'),

    path('p/new', views.ProblemCreate.as_view(), name='problem-create'),
    path('p/<slug>', views.ProblemDetail.as_view(), name='problem'),
    path('p/<slug>/update', views.ProblemUpdateUpload.as_view(), name='problem-update'),
    path('p/<slug>/delete', views.ProblemDelete.as_view(), name='problem-delete'),
    path('p/<slug>/submit', views.ProblemSubmit.as_view(), name='problem-submit'),
    path('p/<slug>/submit/upload', views.ProblemSubmitUpload.as_view(),
         name='problem-submit-upload'),

    path('input/<slug>', views.ProblemDownload.as_view(),
         name='problem-download'),

    path('scoreboard', views.ScoreBoard.as_view(), name='scoreboard'),

    path('submissions', views.SubmissionList.as_view(), name='submissions'),
    path('submissions/<pk>', views.SubmissionDetail.as_view(), name='submission'),
]
