from django.contrib import auth
from django.contrib.auth import forms as authforms
from django.urls import reverse_lazy
from django.views import generic


class LoginView(generic.FormView):
    form_class = authforms.AuthenticationForm
    success_url = reverse_lazy('jam:index')

    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = auth.authenticate(self.request, username=form.cleaned_data['username'],
                                 password=form.cleaned_data['password'])

        auth.login(self.request, user)

        return super(LoginView, self).form_valid(form)


class LogoutView(generic.RedirectView):
    url = reverse_lazy('jam:index')

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class SignupView(generic.FormView):
    form_class = authforms.UserCreationForm
    success_url = reverse_lazy('jam:index')

    template_name = 'registration/login.html'

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return super(SignupView, self).form_valid(form)
