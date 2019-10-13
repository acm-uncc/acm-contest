import datetime

import pytz
from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.urls import reverse


def normalize(submission: str):
    return submission.replace('\r\n', '\n').strip()


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    input = models.TextField(blank=True)
    solution = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse('contest:problem', kwargs=dict(slug=self.slug))

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Score(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    points = models.IntegerField(default=0)

    @property
    def correct_submissions(self):
        return Submission.objects.filter(user=self.user, correct=True)

    @property
    def solved_problems(self):
        return {sub.problem for sub in self.correct_submissions}

    def recompute(self):
        self.points = len(self.solved_problems)
        self.save()

    def __str__(self):
        return f'{self.user.name} score ({self.points} pts)'


class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    time = models.DateTimeField(default=datetime.datetime(1970, 1, 1, tzinfo=pytz.utc))
    submission = models.TextField()
    correct = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('contest:submission', kwargs=dict(pk=self.pk))

    def save(self, *a, **kw):
        self.correct = normalize(self.submission) == normalize(self.problem.solution)
        self.time = datetime.datetime.now()
        super(Submission, self).save(*a, **kw)

        score, created = Score.objects.get_or_create(user=self.user)
        score.recompute()

    def __str__(self):
        return (
            f'{self.user.username} - '
            f'{self.problem.title} ({self.problem.slug}) - '
            f'{"correct" if self.correct else "incorrect"} - '
            f'{self.time:%m/%d/%y %I:%M %p}'
        )
