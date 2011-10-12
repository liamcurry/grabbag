import jingo
import jinja2
from django.conf import settings
from django.utils import html, encoding, formats, timesince
from typogrify.templatetags import jinja2_filters


jinja2_filters.register(jingo.env)


jingo.register.filter(html.linebreaks)
jingo.register.filter(timesince.timesince)
jingo.register.filter(timesince.timeuntil)


@jingo.register.filter
def iriencode(value):
    return encoding.force_unicode(encoding.iri_to_uri(value))


@jingo.register.filter
def date(value, arg=None):
    """Formats a date according to the given format."""
    if not value:
        return u''
    if arg is None:
        arg = settings.DATE_FORMAT
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            from django.utils.dateformat import format
            return format(value, arg)
        except AttributeError:
            return ''


@jingo.register.function
@jinja2.contextfunction
def firstof(context, *args):
    for arg in args:
        if arg:
            return encoding.smart_unicode(arg)
    return ''


@jingo.register.filter
def spaceless(value):
    return jinja2.Markup(' '.join(value.strip('\n').split()))
