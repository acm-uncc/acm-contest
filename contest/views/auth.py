from django.contrib import auth
from django.contrib.auth import forms as authforms
from django.urls import reverse_lazy
from django.views import generic


class SignupView(generic.FormView):
    form_class = authforms.UserCreationForm
    success_url = reverse_lazy('contest:index')

    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return super(SignupView, self).form_valid(form)
