from django import forms
from django.contrib.auth import mixins as authmixins
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic.detail import SingleObjectMixin

from contest import models


class Index(generic.ListView):
    template_name = 'contest/index.html'
    model = models.Problem


class ScoreBoard(generic.TemplateView):
    template_name = 'contest/scoreboard.html'

    def get_context_data(self, **kwargs):
        for score in models.Score.objects.all():
            score.recompute()

        ctx = super(ScoreBoard, self).get_context_data(**kwargs)
        ctx.update(
            users=User.objects.filter(score__points__gt=0).order_by('-score__points'),
            problems=models.Problem.objects.order_by('title')
        )
        return ctx

    #
    # def get_context_data(self, *, object_list=None, **kwargs):
    #
    # def get_queryset(self):
    #     for score in models.Score.objects.all():
    #         score.recompute()
    #     return User.objects.filter(score__points__gt=0).order_by('-score__points')


class ProblemDetail(generic.DetailView):
    model = models.Problem
    template_name = 'contest/problem.html'


class ProblemCreate(authmixins.PermissionRequiredMixin, generic.CreateView):
    permission_required = 'contest.add_problem'

    model = models.Problem
    template_name = 'contest/problem_create.html'

    fields = 'title', 'slug', 'description', 'input', 'solution'


class ProblemCreateUpload(authmixins.PermissionRequiredMixin, generic.CreateView):
    permission_required = 'contest.add_problem'

    model = models.Problem
    template_name = 'contest/problem_create_upload.html'

    form_class = forms.modelform_factory(
        models.Problem,
        fields=('title', 'slug', 'description',
                'input', 'solution'),
        field_classes=(forms.CharField, forms.SlugField, forms.Textarea,
                       forms.FileField, forms.FileField)
    )

    def get_form(self, form_class=None):
        cls = form_class or self.get_form_class()
        return cls(self.request.POST, self.request.FILES)

    def form_valid(self, form):
        form.instance.input = form.files['input'].read().decode('utf-8')
        form.instance.solution = form.files['solution'].read().decode('utf-8')

        return super(ProblemCreateUpload, self).form_valid(form)


class ProblemDelete(authmixins.PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'contest.delete_problem'

    model = models.Problem
    success_url = reverse_lazy('contest:index')


class ProblemUpdate(authmixins.PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'contest.update_problem'

    model = models.Problem
    template_name = 'contest/problem_update.html'

    fields = 'title', 'description', 'input', 'solution'


class ProblemDownload(SingleObjectMixin, generic.View):
    model = models.Problem

    def get(self, request, *args, **kwargs):
        problem = self.get_object()
        return HttpResponse(problem.input, content_type='text/plain; charset=utf8')


class ProblemSubmit(authmixins.LoginRequiredMixin, generic.FormView):
    template_name = 'contest/problem_submit.html'

    form_class = forms.modelform_factory(models.Submission, fields=('submission',))

    submission = None

    def get_context_data(self, **kwargs):
        ctx = super(ProblemSubmit, self).get_context_data(**kwargs)
        ctx['problem'] = models.Problem.objects.get(slug=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        form.instance = models.Submission.objects.create(
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

    form_class = forms.modelform_factory(
        models.Submission,
        fields=('submission',),
        field_classes=(forms.FileField,)
    )

    class form_class(forms.Form):
        submission = forms.FileField()

    def get_form(self, form_class=None):
        cls = form_class or self.get_form_class()
        return cls(self.request.POST, self.request.FILES)

    def form_valid(self, form):
        f = form.files['submission']
        form.instance = models.Submission.objects.create(
            problem=models.Problem.objects.get(slug=self.kwargs['slug']),
            user=User.objects.get(id=self.request.user.id),
            submission=f.read().decode('utf-8')
        )

        form.instance.save()

        self.submission = form.instance

        return super(ProblemSubmit, self).form_valid(form)


class SubmissionDetail(generic.DetailView):
    model = models.Submission
    template_name = 'contest/submission.html'


class SubmissionList(authmixins.LoginRequiredMixin, generic.ListView):
    model = models.Submission
    template_name = 'contest/submissions.html'

    def get_queryset(self):
        return self.model.objects.filter(user__exact=self.request.user)
