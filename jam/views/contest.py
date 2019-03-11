from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from jam import models

from django import forms
from django.contrib.auth import mixins as authmixins


class Index(generic.TemplateView):
    template_name = 'jam/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(Index, self).get_context_data(**kwargs)

        user_scores = [
            (models.user_success(user), user) for user in User.objects.all()
        ]

        top_users = sorted([
            (success, user) for success, user in user_scores
            if success
        ], key=lambda x: x[0], reverse=True)

        ctx.update(
            problems=models.Problem.objects.all(),
            top_users=top_users,
        )
        return ctx


class ProblemDetail(generic.DetailView):
    model = models.Problem
    template_name = 'jam/problem.html'


class ProblemCreate(authmixins.PermissionRequiredMixin, generic.CreateView):
    permission_required = 'jam.add_problem'

    model = models.Problem
    template_name = 'jam/problem_create.html'

    fields = 'title', 'slug', 'description'


class ProblemDelete(authmixins.PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'jam.delete_problem'

    model = models.Problem
    success_url = reverse_lazy('jam:index')


class ProblemUpdate(authmixins.PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'jam.update_problem'

    model = models.Problem
    template_name = 'jam/problem_update.html'

    fields = 'title', 'description'


class PartCreate(authmixins.PermissionRequiredMixin, generic.CreateView):
    permission_required = 'jam.create_part'

    model = models.Part
    template_name = 'jam/part_create.html'

    fields = 'title', 'slug', 'input', 'solution'

    def get_context_data(self, **kwargs):
        ctx = super(PartCreate, self).get_context_data(**kwargs)
        ctx['problem'] = models.Problem.objects.get(slug=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        form.instance.problem = models.Problem.objects.get(slug=self.kwargs['slug'])
        return super(PartCreate, self).form_valid(form)


class PartDelete(authmixins.PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'jam.delete_part'

    model = models.Part

    def get_success_url(self):
        return reverse_lazy('jam:problem', kwargs=dict(slug=self.kwargs['problem']))


class PartDownload(SingleObjectMixin, generic.View):
    model = models.Part

    def get(self, request, *args, **kwargs):
        part = self.get_object()
        return HttpResponse(part.input, content_type='text/plain; charset=utf8')


class ProblemSubmit(authmixins.LoginRequiredMixin, generic.FormView):
    template_name = 'jam/problem_submit.html'

    form_class = forms.modelform_factory(models.Submission, fields=('submission',))

    def get_context_data(self, **kwargs):
        ctx = super(ProblemSubmit, self).get_context_data(**kwargs)
        ctx['problem'] = models.Problem.objects.get(slug=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        form.instance.problem = models.Problem.objects.get(slug=self.kwargs['slug'])
        form.instance.user = self.request.user,
        form.instance.submission = form.cleaned_data['submission']

        return super(ProblemSubmit, self).form_valid(form)


class SubmissionDetail(generic.DetailView):
    model = models.Submission
    template_name = 'jam/submission.html'


class SubmissionList(authmixins.LoginRequiredMixin, generic.ListView):
    model = models.Submission
    template_name = 'jam/submissions.html'

    def get_queryset(self):
        return self.model.objects.filter(user__exact=self.request.user)
