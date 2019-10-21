import bleach
import markdown2
from bleach import ALLOWED_ATTRIBUTES
from django import template
from django.conf import settings
from pygments.styles import get_all_styles

register = template.Library()


@register.filter
def markdown(text):
    text = markdown2.markdown(text, extras=['code-friendly', 'fenced-code-blocks'])
    html = bleach.clean(text, tags=settings.MARKDOWN_FILTER_WHITELIST_TAGS,
                        attributes={'div': ['class'], 'span': ['class']})
    return bleach.linkify(html)
