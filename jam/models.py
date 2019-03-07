from django.db import models
from django.urls import reverse


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    def get_absolute_url(self):
        return reverse('jam:problem', kwargs=dict(slug=self.slug))


class Contest(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    problem = models.ManyToManyField(Problem)
