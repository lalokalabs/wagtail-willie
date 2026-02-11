# wagtail_willie/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import TranslatableMixin
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey


@register_snippet
class CookieCategory(TranslatableMixin, ClusterableModel):
    """Cookie category snippet with multilingual support"""
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text=_("Unique identifier for this category (e.g., 'analytics', 'marketing')")
    )
    title = models.CharField(
        max_length=255,
        help_text=_("Display title for this category")
    )
    description = models.TextField(
        help_text=_("Description of what these cookies do")
    )
    is_required = models.BooleanField(
        default=False,
        help_text=_("If checked, users cannot disable this category")
    )
    order = models.IntegerField(
        default=0,
        help_text=_("Display order (lower numbers appear first)")
    )
    
    panels = [
        FieldPanel('slug'),
        FieldPanel('title'),
        FieldPanel('description'),
        FieldPanel('is_required'),
        FieldPanel('order'),
        InlinePanel('cookies', label=_("Cookies")),
    ]
    
    class Meta(TranslatableMixin.Meta):
        verbose_name = _("Cookie Category")
        verbose_name_plural = _("Cookie Categories")
        ordering = ['order', 'slug']
    
    def __str__(self):
        return self.title


class Cookie(models.Model):
    """Individual cookie within a category"""
    
    category = ParentalKey(
        CookieCategory,
        on_delete=models.CASCADE,
        related_name='cookies'
    )
    name = models.CharField(
        max_length=255,
        help_text=_("Cookie name (e.g., '_ga')")
    )
    description = models.TextField(
        help_text=_("What this cookie does")
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]
    
    class Meta:
        verbose_name = _("Cookie")
        verbose_name_plural = _("Cookies")
        ordering = ['name']
    
    def __str__(self):
        return self.name
