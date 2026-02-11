# Wagtail Willie 🐦

A Django/Wagtail app for managing cookie consent with multilingual support. Part of the Wagtail bird-themed app family (alongside wagtail-starling).

Named after the Willie Wagtail, a charming Australian bird known for its friendly nature and distinctive tail-wagging behavior.

## Features

- ✅ **Wagtail Snippets Integration** - Manage cookie categories and individual cookies through Wagtail admin
- 🌍 **Multilingual Support** - Full translation support using Wagtail's `TranslatableMixin`
- 🍪 **Compact Cookie Storage** - Efficient storage format with timestamps: `analytics=2026-02-10T00:11:49+00:00|marketing=-1`
- 🎨 **Cookie Banner** - Automatic bottom-of-page banner for users without consent
- ⚙️ **Preferences Page** - Dedicated page for granular cookie control
- 🔒 **Required Categories** - Mark certain categories (like "Essential") as mandatory
- 📝 **Template Tags** - Easy-to-use template tags for checking consent
- ⏰ **Timestamp Tracking** - Track when each category was accepted for compliance
- 🎯 **GDPR/Privacy Ready** - Built with privacy regulations in mind

## Installation

1. Install the package:
```bash
pip install wagtail-willie
```

2. Add to your `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'wagtail_willie',
    # ...
]
```

3. Add URL patterns to your main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('cookies/', include('wagtail_willie.urls')),
    # ...
]
```

4. Run migrations:
```bash
python manage.py makemigrations wagtail_willie
python manage.py migrate
```

5. Create cookie categories in Wagtail admin under **Settings > Cookie Categories**

## Quick Start

### 1. Create Cookie Categories

In the Wagtail admin, go to **Settings > Cookie Categories** and create your categories:

**Example: Essential Cookies**
- Slug: `essential`
- Title: `Essential Required`
- Description: `These cookies are necessary for the website to function and cannot be switched off.`
- Is Required: ✓ (checked)
- Order: 0

Add cookies to this category:
- Cookie Name: `sessionid`
- Description: `This cookie is used to maintain your session state across pages.`

**Example: Analytics**
- Slug: `analytics`
- Title: `Analytics`
- Description: `These cookies help us understand how visitors interact with our website by collecting and reporting information anonymously.`
- Is Required: ☐ (unchecked)
- Order: 1

Add cookies:
- `_ga` - Google Analytics cookie used to distinguish users
- `_gid` - Google Analytics cookie used to distinguish users
- `_gat` - Google Analytics cookie used to throttle request rate

**Example: Marketing**
- Slug: `marketing`
- Title: `Marketing`
- Description: `These cookies are used to track visitors across websites and display ads that are relevant and engaging.`
- Is Required: ☐ (unchecked)
- Order: 2

### 2. Add Cookie Banner to Your Base Template

```django
{% load cookie_tags %}
<!DOCTYPE html>
<html>
<head>
    <title>My Site</title>
</head>
<body>
    <!-- Your content -->
    
    <!-- Cookie banner - shows automatically if no consent given -->
    {% cookie_banner %}
</body>
</html>
```

### 3. Use Consent Checks in Templates

```django
{% load cookie_tags %}

<!-- Only load analytics if user has consented -->
{% if accept_cookie "analytics" %}
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
{% endif %}

<!-- Only load marketing pixels if user has consented -->
{% if accept_cookie "marketing" %}
<script>
  // Facebook Pixel, etc.
</script>
{% endif %}

<!-- Check when consent was given -->
{% cookie_consent_timestamp "analytics" as analytics_time %}
{% if analytics_time %}
  <!-- Analytics consent given on: {{ analytics_time|date:"Y-m-d H:i" }} -->
{% endif %}
```

### 4. Link to Cookie Preferences

```django
<a href="{% url 'wagtail_willie:preferences' %}">Cookie Settings</a>
```

## Cookie Storage Format

Consent is stored in a compact format that saves space while tracking timestamps:

```
cookie_consent=analytics=2026-02-10T00:11:49.498057+00:00|marketing=-1|preferences=2026-02-10T00:11:49.498057+00:00
```

- **Accepted categories**: `category_slug=ISO_TIMESTAMP`
- **Declined categories**: `category_slug=-1`
- **Required categories**: Not stored (always considered accepted)

**Examples:**

```
# All declined
analytics=-1|marketing=-1|preferences=-1

# Analytics accepted, others declined
analytics=2026-02-10T00:11:49.498057+00:00|marketing=-1|preferences=-1

# All accepted
analytics=2026-02-10T00:11:49.498057+00:00|marketing=2026-02-10T00:11:49.498057+00:00|preferences=2026-02-10T00:11:49.498057+00:00
```

## Template Tags

### `{% cookie_banner %}`

Renders the cookie consent banner at the bottom of the page. Only shows if user hasn't given consent yet.

```django
{% load cookie_tags %}
{% cookie_banner %}
```

### `{% if accept_cookie "category_slug" %}`

Check if a specific cookie category has been accepted.

```django
{% load cookie_tags %}

{% if accept_cookie "analytics" %}
  <!-- Load analytics code -->
{% endif %}

{% if accept_cookie "marketing" %}
  <!-- Load marketing pixels -->
{% endif %}
```

### `{% cookie_consent_timestamp "category_slug" %}`

Get the timestamp when a category was accepted.

```django
{% load cookie_tags %}

{% cookie_consent_timestamp "analytics" as consent_time %}
{% if consent_time %}
  <p>Analytics consent given on: {{ consent_time|date:"F j, Y" }}</p>
{% endif %}
```

### `{% show_cookie_banner %}`

Check if the cookie banner should be shown (useful for custom implementations).

```django
{% load cookie_tags %}

{% show_cookie_banner as should_show %}
{% if should_show %}
  <div class="custom-cookie-notice">
    <!-- Your custom banner -->
  </div>
{% endif %}
```

## API Reference

### Models

#### `CookieCategory`

Main model for cookie categories (registered as Wagtail snippet).

**Fields:**
- `slug` (SlugField) - Unique identifier used in code (e.g., 'analytics', 'marketing')
- `title` (CharField) - Display name shown to users
- `description` (TextField) - Explanation of what these cookies do
- `is_required` (BooleanField) - If True, users cannot disable this category
- `order` (IntegerField) - Display order (lower numbers first)

**Relations:**
- `cookies` - Related `Cookie` objects in this category

**Meta:**
- Supports translations via `TranslatableMixin`
- Ordered by `order`, then `slug`

#### `Cookie`

Individual cookies within a category.

**Fields:**
- `category` (ForeignKey) - Parent `CookieCategory`
- `name` (CharField) - Cookie name (e.g., '_ga', 'sessionid')
- `description` (TextField) - What this cookie does

### Utility Functions

#### `encode_consent(consent_dict)`

Encode a consent dictionary to the compact string format.

```python
from wagtail_willie.utils import encode_consent

consent = {
    'analytics': True,
    'marketing': False,
    'preferences': True
}
encoded = encode_consent(consent)
# Returns: "analytics=2026-02-10T00:11:49+00:00|marketing=-1|preferences=2026-02-10T00:11:49+00:00"
```

#### `decode_consent(consent_string)`

Decode a consent string back to a dictionary.

```python
from wagtail_willie.utils import decode_consent

consent_string = "analytics=2026-02-10T00:11:49+00:00|marketing=-1"
consent = decode_consent(consent_string)
# Returns: {'essential': True, 'analytics': True, 'marketing': False, ...}
```

#### `get_consent_from_request(request)`

Get the full consent dictionary from a request object.

```python
from wagtail_willie.utils import get_consent_from_request

def my_view(request):
    consent = get_consent_from_request(request)
    if consent.get('analytics'):
        # Track analytics
        pass
```

#### `get_consent_timestamp(consent_string, category_slug)`

Get the timestamp when a specific category was accepted.

```python
from wagtail_willie.utils import get_consent_timestamp

consent_string = request.COOKIES.get('cookie_consent', '')
timestamp = get_consent_timestamp(consent_string, 'analytics')
# Returns: datetime object or None
```

## Views

### Cookie Preferences View

URL: `/cookies/preferences/`  
Name: `wagtail_willie:preferences`

Displays the cookie preferences page where users can accept/decline individual categories.

**Query Parameters:**
- `next` - Redirect URL after saving preferences (default: `/`)

### Cookie Banner Action View

URL: `/cookies/banner/`  
Name: `wagtail_willie:banner`

Handles "Accept All" and "Decline All" actions from the banner.

**POST Parameters:**
- `action` - Either `accept_all` or `decline_all`
- `next` - Redirect URL after action (default: `/`)

### Accept Category View

URL: `/cookies/accept/<category_slug>/`  
Name: `wagtail_willie:accept_category`

Accepts a specific cookie category without affecting other categories.

**POST Parameters:**
- `next` - Redirect URL after action (default: `/`)

### Decline Category View

URL: `/cookies/decline/<category_slug>/`  
Name: `wagtail_willie:decline_category`

Declines a specific cookie category without affecting other categories.

**POST Parameters:**
- `next` - Redirect URL after action (default: `/`)

## Customization

### Custom Cookie Banner

Replace the default banner with your own design:

```django
{% load cookie_tags %}

{% show_cookie_banner as should_show %}
{% if should_show %}
<div class="my-custom-banner">
    <p>We use cookies to improve your experience.</p>
    
    <form method="post" action="{% url 'wagtail_willie:banner' %}">
        {% csrf_token %}
        <input type="hidden" name="next" value="{{ request.path }}">
        
        <button type="submit" name="action" value="accept_all">
            Accept All
        </button>
        
        <button type="submit" name="action" value="decline_all">
            Decline All
        </button>
        
        <a href="{% url 'wagtail_willie:preferences' %}?next={{ request.path }}">
            Customize
        </a>
    </form>
</div>
{% endif %}
```

### Custom Preferences with Individual Category Actions

You can create accept/decline buttons for each category:

```django
{% load cookie_tags %}

{% for category in categories %}
<div class="cookie-category">
    <h3>{{ category.title }}</h3>
    <p>{{ category.description }}</p>
    
    {% if not category.is_required %}
        {% if current_consent|get_item:category.slug %}
            <span>Accepted</span>
            <form method="post" action="{% url 'wagtail_willie:decline_category' category.slug %}">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ request.path }}">
                <button type="submit">Decline</button>
            </form>
        {% else %}
            <span>Declined</span>
            <form method="post" action="{% url 'wagtail_willie:accept_category' category.slug %}">
                {% csrf_token %}
                <input type="hidden" name="next" value="{{ request.path }}">
                <button type="submit">Accept</button>
            </form>
        {% endif %}
    {% else %}
        <span>Required - Always Active</span>
    {% endif %}
</div>
{% endfor %}
```

### Custom Preferences Template

Override the template by creating your own at:
```
templates/wagtail_willie/cookie_preferences.html
```

### Styling

The default templates use inline styles for zero dependencies. Override the templates or add your own CSS:

```css
/* Custom cookie banner styles */
#cookie-banner {
    /* Your styles */
}
```

## Multilingual Setup

Wagtail Willie uses Wagtail's translation system. To add translations:

1. Enable Wagtail's internationalization in `settings.py`:

```python
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', 'English'),
    ('es', 'Spanish'),
    ('fr', 'French'),
]
```

2. Create translations for each cookie category in the Wagtail admin by using the locale selector.

3. Django's standard translation system handles UI strings:

```bash
python manage.py makemessages -l es
python manage.py compilemessages
```

## GDPR Compliance

Wagtail Willie helps with GDPR compliance by:

- ✅ **Explicit Consent** - Users must actively accept cookies
- ✅ **Granular Control** - Users can accept/decline by category
- ✅ **Timestamp Tracking** - Records when consent was given
- ✅ **Easy Withdrawal** - Users can change preferences anytime
- ✅ **Required Categories** - Only truly essential cookies are mandatory
- ✅ **Transparent Information** - Clear descriptions of what each cookie does

**Important:** While Wagtail Willie provides the tools for cookie consent, you are responsible for:
- Writing accurate cookie descriptions
- Properly categorizing cookies
- Only loading scripts after consent is given
- Maintaining compliance with applicable laws

## Common Patterns

### Loading Third-Party Scripts Conditionally

```django
{% load cookie_tags %}

<!-- Google Analytics -->
{% if accept_cookie "analytics" %}
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
{% endif %}

<!-- Facebook Pixel -->
{% if accept_cookie "marketing" %}
<script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', 'YOUR_PIXEL_ID');
  fbq('track', 'PageView');
</script>
{% endif %}

<!-- Matomo -->
{% if accept_cookie "analytics" %}
<script>
  var _paq = window._paq = window._paq || [];
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {
    var u="//your-matomo-url/";
    _paq.push(['setTrackerUrl', u+'matomo.php']);
    _paq.push(['setSiteId', 'YOUR_SITE_ID']);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.async=true; g.src=u+'matomo.js'; s.parentNode.insertBefore(g,s);
  })();
</script>
{% endif %}
```

### Checking Consent in Python Views

```python
from wagtail_willie.utils import get_consent_from_request

def my_view(request):
    consent = get_consent_from_request(request)
    
    if consent.get('analytics'):
        # Track this page view in your analytics system
        track_page_view(request)
    
    if consent.get('marketing'):
        # Show personalized ads
        ads = get_personalized_ads(request.user)
    else:
        # Show generic ads
        ads = get_generic_ads()
    
    return render(request, 'template.html', {'ads': ads})
```

### Custom Middleware for Analytics

```python
# middleware.py
from wagtail_willie.utils import get_consent_from_request

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        consent = get_consent_from_request(request)
        request.analytics_enabled = consent.get('analytics', False)
        request.marketing_enabled = consent.get('marketing', False)
        
        response = self.get_response(request)
        return response
```

Then in views:
```python
def my_view(request):
    if request.analytics_enabled:
        # Track analytics
        pass
```

## Troubleshooting

### Banner Not Showing

1. Check that you've added `{% load cookie_tags %}` at the top of your template
2. Verify that `{% cookie_banner %}` is in your base template
3. Clear your browser cookies for the site
4. Check browser console for JavaScript errors

### Consent Not Persisting

1. Check that cookies are enabled in the browser
2. Verify that your site is served over HTTPS (required for `SameSite=Lax`)
3. Check cookie settings in browser dev tools
4. Ensure no cookie blocker extensions are active

### Categories Not Showing in Admin

1. Run migrations: `python manage.py migrate wagtail_willie`
2. Restart your development server
3. Clear cache if using caching
4. Check that `wagtail_willie` is in `INSTALLED_APPS`

### Template Tag Not Working

```django
{# Wrong - missing load statement #}
{% if accept_cookie "analytics" %}

{# Correct #}
{% load cookie_tags %}
{% if accept_cookie "analytics" %}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Credits

Part of the Wagtail bird-themed app ecosystem:
- **wagtail-starling** - Extra Wagtail functionality
- **wagtail-willie** - Cookie consent management (this package)

Named after the Willie Wagtail (*Rhipidura leucophrys*), a passerine bird native to Australia, New Guinea, and the Solomon Islands.

## Changelog

### 1.0.0 (2026-02-11)
- Initial release
- Cookie category management via Wagtail snippets
- Multilingual support
- Compact timestamp-based consent storage
- Cookie banner and preferences page
- Template tags for consent checking
```
