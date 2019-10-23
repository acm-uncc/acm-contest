from django import template
from contest.models import Score

register = template.Library()

register.filter('time', Score.get_time)


@register.filter
def attempts(score, problem):
    try:
        attempts = score.get_bad_attempts(problem)
        if is_solved(score, problem):
            attempts += 1
        return attempts
    except AttributeError:
        return False


@register.filter
def is_solved(score, problem):
    try:
        return score.get_first_solution(problem) is not None
    except AttributeError:
        return False
