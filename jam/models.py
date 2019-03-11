from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.urls import reverse


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField(max_length=10_000)

    def get_absolute_url(self):
        return reverse('jam:problem', kwargs=dict(slug=self.slug))

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Part(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=False)

    input = models.TextField(max_length=10_000, blank=True)
    solution = models.TextField(max_length=10_000, blank=True)

    def get_absolute_url(self):
        return self.problem.get_absolute_url()


class Submission(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    submission = models.TextField(max_length=10_000)

    @property
    def correct(self):
        return self.submission == self.part.solution

    def get_absolute_url(self):
        return reverse('jam:submission', kwargs=dict(pk=self.pk))


def user_success(user):
    success = {
        sub.problem
        for sub in user.submission_set.all()
        if sub.correct
    }

    return success
