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
