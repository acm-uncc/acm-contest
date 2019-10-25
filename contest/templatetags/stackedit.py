import re

import bleach
import markdown2
from django import template
from django.conf import settings

register = template.Library()


@register.filter
def katex(text):
    def escaper(m):
        return re.sub(r'([*_])', r'\\\1', m[0])

    return re.sub(r'(\${1,2}).*?\1', escaper, text)


@register.filter
def markdown(text):
    text = katex(text)
    text = markdown2.markdown(text, extras=['code-friendly', 'fenced-code-blocks'])
    text = bleach.clean(text, tags=settings.MARKDOWN_FILTER_WHITELIST_TAGS, attributes={
        'div': ['class'],
        'span': ['class'],
        'img': ['src', 'title']
    })
    text = bleach.linkify(text)
    return text
