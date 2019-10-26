from django import forms
from django.contrib.auth import mixins as authmixins
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from contest import models


class Index(generic.ListView):
    template_name = 'contest/index.html'
    context_object_name = 'contests'

    def get_queryset(self):
        return models.Contest.active()


class ScoreBoard(generic.TemplateView):
    template_name = 'contest/scoreboard.html'

    def get_context_data(self, **kwargs):
        for score in models.Score.objects.all():
            score.recompute()

        ctx = super(ScoreBoard, self).get_context_data(**kwargs)
        ctx.update(
            users=User.objects.order_by('-score__points', 'score__minutes',
                                        'username').filter(score__points__gt=0),
            contests=models.Contest.active()
        )
        return ctx


class ContestRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not models.Contest.active():
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)


class ProblemDetail(ContestRequiredMixin, generic.DetailView):
    model = models.Problem
    template_name = 'contest/problem.html'

    def get_queryset(self):
        return self.model.objects.defer('input', 'solution')


class ProblemCreate(authmixins.PermissionRequiredMixin, generic.CreateView):
    permission_required = 'contest.add_problem'

    model = models.Problem
    template_name = 'contest/problem_create.html'

    form_class = forms.modelform_factory(
        models.Problem,
        fields=('title', 'slug', 'description',
                'input', 'solution'),
        field_classes=(forms.CharField, forms.SlugField, forms.Textarea,
                       forms.FileField, forms.FileField)
    )

    def form_valid(self, form):
        if 'input' in form.files:
            form.instance.input = form.files['input'].read().decode('utf-8')
        else:
            form.instance.input = ''

        if 'solution' in form.files:
            form.instance.solution = form.files['solution'].read().decode('utf-8')
        else:
            form.instance.input = ''

        return super(ProblemCreate, self).form_valid(form)


class ProblemUpdateUpload(authmixins.PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'contest.update_problem'

    model = models.Problem
    template_name = 'contest/problem_update.html'

    form_class = forms.modelform_factory(
        models.Problem,
        fields=('title', 'slug', 'description',
                'input', 'solution'),
        field_classes=(forms.CharField, forms.SlugField, forms.Textarea)
    )

    def form_valid(self, form):
        obj = self.get_object()

        if 'input' in form.files:
            form.instance.input = form.files['input'].read().decode('utf-8')
        else:
            form.instance.input = obj.input

        if 'solution' in form.files:
            form.instance.solution = form.files['solution'].read().decode('utf-8')
        else:
            form.instance.solution = obj.solution

        return super(ProblemUpdateUpload, self).form_valid(form)


class ProblemDelete(authmixins.PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'contest.delete_problem'

    model = models.Problem
    success_url = reverse_lazy('contest:index')


class ProblemDownload(ContestRequiredMixin, SingleObjectMixin, generic.View):
    model = models.Problem

    def get(self, request, *args, **kwargs):
        problem = self.get_object()
        return HttpResponse(problem.input, content_type='text/plain; charset=utf8')


class ProblemSubmit(ContestRequiredMixin, authmixins.LoginRequiredMixin,
                    generic.FormView):
    template_name = 'contest/problem_submit.html'

    class SubmissionForm(forms.Form):
        submission = forms.CharField(widget=forms.Textarea)

    form_class = SubmissionForm

    submission = None

    def get_context_data(self, **kwargs):
        ctx = super(ProblemSubmit, self).get_context_data(**kwargs)
        ctx['problem'] = models.Problem.objects.get(slug=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        form.instance = models.Submission.grade(
            problem=models.Problem.objects.get(slug=self.kwargs['slug']),
            user=self.request.user,
            submission=form.cleaned_data['submission']
        )
        form.instance.save()

        self.submission = form.instance

        return super(ProblemSubmit, self).form_valid(form)

    def get_success_url(self):
        return self.submission.get_absolute_url()


class ProblemSubmitUpload(ProblemSubmit):
    template_name = 'contest/problem_submit_upload.html'

    class SubmissionForm(forms.Form):
        submission = forms.FileField()

    form_class = SubmissionForm

    def form_valid(self, form):
        sub = form.files['submission'].read().decode('utf-8')
        form.cleaned_data['submission'] = sub

        return super(ProblemSubmitUpload, self).form_valid(form)


class SubmissionDetail(generic.DetailView):
    model = models.Submission
    template_name = 'contest/submission.html'


class SubmissionList(authmixins.LoginRequiredMixin, generic.ListView):
    model = models.Submission
    template_name = 'contest/submissions.html'

    def get_queryset(self):
        return self.model.objects.filter(user__exact=self.request.user)
