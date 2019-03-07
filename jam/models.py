from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.urls import reverse


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    difficulty = models.IntegerField()

    description = models.TextField(max_length=10_000)
    solution = models.TextField(max_length=10_000)

    def get_absolute_url(self):
        return reverse('jam:problem', kwargs=dict(slug=self.slug))

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    submission = models.TextField(max_length=10_000)

    @property
    def correct(self):
        return self.submission == self.problem.solution

    def get_absolute_url(self):
        return reverse('jam:submission', kwargs=dict(pk=self.pk))


def user_success(user):
    success = {
        sub.problem
        for sub in user.submission_set.all()
        if sub.correct
    }

    return success
