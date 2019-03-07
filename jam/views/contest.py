from django.urls import reverse_lazy
from django.views import generic

from jam import models

from django.contrib.auth import mixins as authmixins


class Index(generic.TemplateView):
    template_name = 'jam/index.html'

    def get_context_data(self, **kwargs):
        ctx = super(Index, self).get_context_data(**kwargs)
        ctx.update(
            problems=models.Problem.objects.all()
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

    def get_form(self, form_class=None):
        form = super(ProblemCreate, self).get_form(form_class)

        return form


class ProblemDelete(authmixins.PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'jam.delete_problem'

    model = models.Problem
    success_url = reverse_lazy('jam:index')
