from django.urls import path
from .views import (
    CookiePreferencesView, 
    CookieBannerActionView,
    AcceptCategoryView,
    DeclineCategoryView
)

app_name = 'wagtail_willie'

urlpatterns = [
    path('preferences/', CookiePreferencesView.as_view(), name='preferences'),
    path('banner/', CookieBannerActionView.as_view(), name='banner'),
    path('accept/<slug:category_slug>/', AcceptCategoryView.as_view(), name='accept_category'),
    path('decline/<slug:category_slug>/', DeclineCategoryView.as_view(), name='decline_category'),
]
