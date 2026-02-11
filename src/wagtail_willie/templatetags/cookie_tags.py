from django import template
from wagtail_willie.utils import get_consent_from_request, get_consent_timestamp

register = template.Library()


@register.filter(name="get_item")
def get_item(dictionary, key):
    """
    Get item from dictionary by key
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.simple_tag(takes_context=True)
def accept_cookie(context, category_slug):
    """
    Check if a cookie category is accepted
    Usage: {% if accept_cookie "analytics" %}...{% endif %}
    
    Args:
        category_slug: The slug of the cookie category to check
    """
    request = context.get('request')
    if not request:
        return False
    
    consent = get_consent_from_request(request)
    return consent.get(category_slug, False)


@register.simple_tag(takes_context=True)
def cookie_consent_timestamp(context, category_slug):
    """
    Get the timestamp when a cookie category was accepted
    Usage: {% cookie_consent_timestamp "analytics" %}
    
    Args:
        category_slug: The slug of the cookie category
    
    Returns:
        datetime object or None
    """
    request = context.get('request')
    if not request:
        return None
    
    consent_string = request.COOKIES.get('cookie_consent', '')
    return get_consent_timestamp(consent_string, category_slug)


@register.simple_tag(takes_context=True)
def show_cookie_banner(context):
    """
    Check if cookie banner should be shown
    Usage: {% show_cookie_banner as show_banner %}
    """
    request = context.get('request')
    if not request:
        return True
    
    return 'cookie_consent' not in request.COOKIES


@register.inclusion_tag('wagtail_willie/cookie_banner.html', takes_context=True)
def cookie_banner(context):
    """
    Render cookie banner if consent not given
    Usage: {% cookie_banner %}
    """
    request = context.get('request')
    show_banner = 'cookie_consent' not in request.COOKIES if request else True
    
    return {
        'show_banner': show_banner,
        'request': request,
    }
