from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.views import generic

from jam import models


class Index(generic.TemplateView):
    template_name = 'jam/index.html'


class ProblemList(generic.ListView):
    template_name = 'jam/problem_list.html'

    model = models.Problem


class ProblemCreate(generic.CreateView):
    template_name = 'jam/problem_create.html'

    model = models.Problem
    fields = 'title', 'slug'

    def get_context_data(self, **kwargs):
        helper = FormHelper()
        helper.add_input(Submit('submit', 'Submit'))

        data = super(ProblemCreate, self).get_context_data(**kwargs).copy()
        data.update(helper=helper)
        return data


class ProblemDetail(generic.DetailView):
    template_name = 'jam/problem_detail.html'

    model = models.Problem
