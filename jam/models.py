from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.urls import reverse


def normalize(submission: str):
    return submission.replace('\r\n', '\n').strip()


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    def get_absolute_url(self):
        return reverse('jam:problem', kwargs=dict(slug=self.slug))

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Part(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    slug = models.SlugField()
    points = models.IntegerField()

    input = models.TextField(blank=True)
    solution = models.TextField(blank=True)

    def get_absolute_url(self):
        return self.problem.get_absolute_url()


class Score(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    points = models.IntegerField(default=0)

    def recompute(self):
        subs = Submission.objects.filter(user=self.user, correct=True)
        parts = {sub.part for sub in subs}
        self.points = sum(part.points for part in parts)
        self.save()


class Submission(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    submission = models.TextField()
    correct = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('jam:submission', kwargs=dict(pk=self.pk))

    def save(self, *a, **kw):
        self.correct = normalize(self.submission) == normalize(self.part.solution)
        super(Submission, self).save(*a, **kw)

        score, created = Score.objects.get_or_create(user=self.user)
        score.recompute()
