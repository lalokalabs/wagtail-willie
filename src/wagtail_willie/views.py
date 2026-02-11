from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from wagtail.models import Locale
from .models import CookieCategory
from .utils import encode_consent, decode_consent, get_consent_from_request, update_consent


class CookiePreferencesView(View):
    """View for managing cookie preferences"""
    
    template_name = 'wagtail_willie/cookie_preferences.html'
    
    def get(self, request):
        categories = CookieCategory.objects.filter(locale=Locale.get_active())
        current_consent = get_consent_from_request(request)
        
        # Get consent string for displaying timestamps
        consent_string = request.COOKIES.get('cookie_consent', '')
        
        context = {
            'categories': categories,
            'current_consent': current_consent,
            'consent_string': consent_string,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Process consent form
        consent = {}
        categories = CookieCategory.objects.filter(locale=Locale.get_active())
        
        for category in categories:
            if category.is_required:
                consent[category.slug] = True
            else:
                consent[category.slug] = request.POST.get(f'category_{category.slug}') == 'on'
        
        # Encode and store consent in cookie (valid for 1 year)
        consent_string = encode_consent(consent)
        response = redirect(request.POST.get('next', '/'))
        response.set_cookie(
            'cookie_consent',
            consent_string,
            max_age=365 * 24 * 60 * 60,  # 1 year
            path='/',  # Available across entire site
            httponly=False,  # Needs to be readable by JavaScript
            samesite='Lax'
        )
        
        return response


class CookieBannerActionView(View):
    """Handle accept all / decline all actions from banner"""
    
    def post(self, request):
        action = request.POST.get('action')
        categories = CookieCategory.objects.filter(locale=Locale.get_active())
        consent = {}
        
        for category in categories:
            if action == 'accept_all':
                consent[category.slug] = True
            elif action == 'decline_all':
                consent[category.slug] = category.is_required
        
        consent_string = encode_consent(consent)
        response = redirect(request.POST.get('next', '/'))
        response.set_cookie(
            'cookie_consent',
            consent_string,
            max_age=365 * 24 * 60 * 60,
            path='/',  # Available across entire site
            httponly=False,
            samesite='Lax'
        )
        
        return response


class AcceptCategoryView(View):
    """Handle accepting a specific cookie category"""
    
    def post(self, request, category_slug):
        category = get_object_or_404(
            CookieCategory,
            slug=category_slug,
            locale=Locale.get_active()
        )
        
        # Don't allow changing required categories
        if category.is_required:
            return redirect(request.POST.get('next', '/'))
        
        # Update consent for this category only
        existing_consent = request.COOKIES.get('cookie_consent', '')
        updated_consent = update_consent(existing_consent, category_slug, accepted=True)
        
        response = redirect(request.POST.get('next', '/'))
        response.set_cookie(
            'cookie_consent',
            updated_consent,
            max_age=365 * 24 * 60 * 60,
            path='/',  # Available across entire site
            httponly=False,
            samesite='Lax'
        )
        
        return response


class DeclineCategoryView(View):
    """Handle declining a specific cookie category"""
    
    def post(self, request, category_slug):
        category = get_object_or_404(
            CookieCategory,
            slug=category_slug,
            locale=Locale.get_active()
        )
        
        # Don't allow declining required categories
        if category.is_required:
            return redirect(request.POST.get('next', '/'))
        
        # Update consent for this category only
        existing_consent = request.COOKIES.get('cookie_consent', '')
        updated_consent = update_consent(existing_consent, category_slug, accepted=False)
        
        response = redirect(request.POST.get('next', '/'))
        response.set_cookie(
            'cookie_consent',
            updated_consent,
            max_age=365 * 24 * 60 * 60,
            path='/',  # Available across entire site
            httponly=False,
            samesite='Lax'
        )
        
        return response
