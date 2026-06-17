from django.db import models
from django.contrib import admin
from .models import NewsletterSubscriber, PlatformTestimonial

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    ordering = ('-subscribed_at',)

@admin.register(PlatformTestimonial)
class PlatformTestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_featured', 'created_at')
    list_editable = ('is_featured',)
    list_filter = ('is_featured', 'rating', 'created_at')
    search_fields = ('user__username', 'content')
    ordering = ('-created_at',)
