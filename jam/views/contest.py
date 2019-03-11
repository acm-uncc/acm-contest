from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from jam import models

from django import forms
from django.contrib.auth import mixins as authmixins


class Index(generic.TemplateView):
    template_name = 'jam/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(Index, self).get_context_data(**kwargs)

        # top_users = User.objects.annotate(
        #     num_submissions=Count(
        #         'submission',
        #         filter=Q(
        #             submission__correct=True
        #         )
        #     )
        # ).order_by(
        #     '-num_submissions'
        # )[:5]

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

    fields = 'title', 'slug', 'difficulty', 'description', 'solution'


class ProblemDelete(authmixins.PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'jam.delete_problem'

    model = models.Problem
    success_url = reverse_lazy('jam:index')


class ProblemUpdate(authmixins.PermissionRequiredMixin, generic.UpdateView):
    permission_required = 'jam.update_problem'

    model = models.Problem
    template_name = 'jam/problem_update.html'

    fields = 'title', 'difficulty', 'description', 'solution'


class ProblemSubmit(authmixins.LoginRequiredMixin, generic.FormView):
    template_name = 'jam/problem_submit.html'

    form_class = forms.modelform_factory(models.Submission, fields=('submission',))

    def get_success_url(self):
        return reverse_lazy('jam:problem', kwargs=dict(slug=self.kwargs['slug']))

    def get_context_data(self, **kwargs):
        ctx = super(ProblemSubmit, self).get_context_data(**kwargs)
        ctx['problem'] = models.Problem.objects.get(slug=self.kwargs['slug'])
        return ctx

    def form_valid(self, form):
        problem = models.Problem.objects.get(slug=self.kwargs['slug'])

        sub = models.Submission.objects.create(
            problem=problem,
            user=self.request.user,
            submission=form.cleaned_data['submission'],
        )
        sub.save()

        return redirect(sub.get_absolute_url())


class SubmissionDetail(generic.DetailView):
    model = models.Submission
    template_name = 'jam/submission.html'


class SubmissionList(authmixins.LoginRequiredMixin, generic.ListView):
    model = models.Submission
    template_name = 'jam/submissions.html'

    def get_queryset(self):
        return self.model.objects.filter(user__exact=self.request.user)
