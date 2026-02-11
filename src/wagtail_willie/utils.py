from datetime import datetime
from django.utils import timezone
from .models import CookieCategory


def encode_consent(consent_dict):
    """
    Encode consent dictionary to compact string format with timestamps.
    Format: "category1=timestamp|category2=-1|category3=timestamp"
    
    Example: 
    {
        'analytics': True, 
        'marketing': False, 
        'preferences': True
    } 
    -> "analytics=2026-02-10T00:11:49.498057+00:00|marketing=-1|preferences=2026-02-10T00:11:49.498057+00:00"
    
    -1 means declined/not accepted
    ISO timestamp means accepted at that time
    Required categories are not stored (always considered accepted)
    
    Returns "CONSENT_GIVEN" if all categories are required and no optional ones exist,
    to ensure cookie banner is hidden.
    """
    categories = CookieCategory.objects.all()
    parts = []
    now = timezone.now().isoformat()
    
    for category in categories:
        # Skip required categories - they're always accepted
        if category.is_required:
            continue
            
        if consent_dict.get(category.slug, False):
            parts.append(f"{category.slug}={now}")
        else:
            parts.append(f"{category.slug}=-1")
    
    # If no parts (all categories required), return marker to hide banner
    if not parts:
        return 'CONSENT_GIVEN'
    
    return '|'.join(parts)


def decode_consent(consent_string):
    """
    Decode consent string to dictionary format.
    
    Example: 
    "analytics=2026-02-10T00:11:49.498057+00:00|marketing=-1" 
    -> {
        'essential': True,  # Required category
        'analytics': True, 
        'marketing': False
    }
    
    Handles special marker "CONSENT_GIVEN" for when all categories are required.
    
    Returns dict with all categories and their consent status.
    """
    consent = {}
    categories = CookieCategory.objects.all()
    
    # Parse the consent string (skip if special marker)
    consent_data = {}
    if consent_string and consent_string != 'CONSENT_GIVEN':
        for part in consent_string.split('|'):
            if '=' in part:
                slug, value = part.split('=', 1)
                consent_data[slug] = value
    
    # Build full consent dictionary
    for category in categories:
        if category.is_required:
            # Required categories are always accepted
            consent[category.slug] = True
        else:
            # Check if category has consent data
            value = consent_data.get(category.slug, '-1')
            consent[category.slug] = value != '-1'
    
    return consent


def get_consent_timestamp(consent_string, category_slug):
    """
    Get the timestamp when a category was accepted.
    Returns datetime object or None if not accepted or declined.
    
    Example:
    consent_string = "analytics=2026-02-10T00:11:49.498057+00:00|marketing=-1"
    get_consent_timestamp(consent_string, 'analytics') -> datetime(2026, 2, 10, 0, 11, 49, 498057)
    get_consent_timestamp(consent_string, 'marketing') -> None
    """
    if not consent_string:
        return None
    
    for part in consent_string.split('|'):
        if '=' in part:
            slug, value = part.split('=', 1)
            if slug == category_slug and value != '-1':
                try:
                    return datetime.fromisoformat(value)
                except (ValueError, AttributeError):
                    return None
    
    return None


def get_consent_from_request(request):
    """
    Helper function to get consent dictionary from request.
    Returns dict with all categories and their consent status.
    """
    consent_cookie = request.COOKIES.get('cookie_consent', '')
    return decode_consent(consent_cookie)


def update_consent(existing_consent_string, category_slug, accepted):
    """
    Update a single category's consent status in existing consent string.
    Useful for updating consent without losing timestamps of other categories.
    
    Args:
        existing_consent_string: Current consent cookie value
        category_slug: Category to update
        accepted: Boolean indicating if accepted
    
    Returns:
        Updated consent string
    """
    # Parse existing consent
    consent_data = {}
    if existing_consent_string:
        for part in existing_consent_string.split('|'):
            if '=' in part:
                slug, value = part.split('=', 1)
                consent_data[slug] = value
    
    # Update the specific category
    if accepted:
        consent_data[category_slug] = timezone.now().isoformat()
    else:
        consent_data[category_slug] = '-1'
    
    # Rebuild string
    parts = [f"{slug}={value}" for slug, value in consent_data.items()]
    return '|'.join(parts)
