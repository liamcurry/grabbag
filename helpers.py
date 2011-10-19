"""
Some of these are lifted from Mozilla's Funfactory.
"""
import jingo
import jinja2
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import defaultfilters
from django.utils import html, encoding, formats, timesince
from typogrify.templatetags import jinja2_filters


jinja2_filters.register(jingo.env)


jingo.register.filter(html.linebreaks)
jingo.register.filter(timesince.timesince)
jingo.register.filter(timesince.timeuntil)
jingo.register.filter(defaultfilters.timesince)
jingo.register.filter(defaultfilters.truncatewords)


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


@jingo.register.function
def thisyear():
    """The current year."""
    return jinja2.Markup(datetime.date.today().year)


@jingo.register.function
def url(viewname, *args, **kwargs):
    """Helper for Django's ``reverse`` in templates."""
    return reverse(viewname, args=args, kwargs=kwargs)


@jingo.register.filter
def urlparams(url_, hash=None, **query):
    """Add a fragment and/or query paramaters to a URL.

    New query params will be appended to exising parameters, except duplicate
    names, which will be replaced.
    """
    url = urlparse.urlparse(url_)
    fragment = hash if hash is not None else url.fragment

    # Use dict(parse_qsl) so we don't get lists of values.
    q = url.query
    query_dict = dict(urlparse.parse_qsl(smart_str(q))) if q else {}
    query_dict.update((k, v) for k, v in query.items())

    query_string = _urlencode([(k, v) for k, v in query_dict.items()
                               if v is not None])
    new = urlparse.ParseResult(url.scheme, url.netloc, url.path, url.params,
                               query_string, fragment)
    return new.geturl()

def _urlencode(items):
    """A Unicode-safe URLencoder."""
    try:
        return urllib.urlencode(items)
    except UnicodeEncodeError:
        return urllib.urlencode([(k, smart_str(v)) for k, v in items])


@jingo.register.filter
def urlencode(txt):
    """Url encode a path."""
    return urllib.quote_plus(txt)
