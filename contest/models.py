import datetime

import pytz
from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.urls import reverse
from django.utils import timezone


def normalize(submission: str):
    return submission.replace('\r\n', '\n').strip()


class Problem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    input = models.TextField(null=True, blank=True)
    solution = models.TextField(null=True, blank=True)

    def get_deferred_fields(self):
        pass

    def get_absolute_url(self):
        return reverse('contest:problem', kwargs=dict(slug=self.slug))

    def __str__(self):
        return f'{self.title} ({self.slug})'


class Contest(models.Model):
    title = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()

    problems = models.ManyToManyField(Problem)

    @classmethod
    def active(cls):
        now = datetime.datetime.now()
        return cls.objects.filter(start__lt=now, end__gt=now)

    @classmethod
    def started(cls):
        now = datetime.datetime.now()
        return cls.objects.filter(start__lt=now)

    @property
    def is_active(self):
        return self.start < datetime.datetime.now() < self.end

    @property
    def problem_list(self):
        return self.problems.defer('solution', 'input', 'description').order_by('title')

    def __str__(self):
        state = 'active' if self.is_active else 'inactive'
        return f'{self.title!r} ({state})'


class Score(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    points = models.IntegerField(default=0)
    minutes = models.IntegerField(default=0)

    @property
    def deferred_submissions(self):
        return Submission.objects.defer(
            'problem__input', 'problem__solution'
        )

    @property
    def correct_submissions(self):
        return self.deferred_submissions.filter(user=self.user, correct=True)

    @property
    def solved_problems(self):
        return {sub.problem for sub in self.correct_submissions}

    def get_first_solution(self, problem):
        solved = self.deferred_submissions.filter(user=self.user, problem=problem,
                                                  correct=True).order_by('time')
        if solved:
            return solved[0]
        return None

    def get_bad_attempts(self, problem):
        first_solution = self.get_first_solution(problem)
        if first_solution is None:
            attempts = Submission.objects.defer(
                'problem__input', 'problem__solution'
            ).filter(user=self.user, problem=problem, correct=False)
        else:
            attempts = self.deferred_submissions.filter(user=self.user, problem=problem,
                                                        correct=False,
                                                        time__lt=first_solution.time)
        return len(attempts)

    def get_time(self, problem):
        solution = self.get_first_solution(problem)
        penalty = 20 * self.get_bad_attempts(problem)

        if not solution:
            return penalty

        active = Contest.active()
        if not active:
            return penalty

        start = active[0].start

        minutes = (solution.time - start).seconds // 60
        return minutes + penalty

    def recompute(self):
        self.points = len(self.solved_problems)
        self.minutes = sum(self.get_time(p) for p in self.solved_problems)
        self.save()

    def __str__(self):
        return f'{self.user} score ({self.points} pts)'


class Submission(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    time = models.DateTimeField(default=datetime.datetime(1970, 1, 1, tzinfo=pytz.utc))
    correct = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('contest:submission', kwargs=dict(pk=self.pk))

    @classmethod
    def grade(cls, problem, user, submission):
        correct = normalize(problem.solution) == normalize(submission)
        now = datetime.datetime.now()

        return cls(problem=problem, user=user, time=now, correct=correct)

    def save(self, *a, **kw):
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
