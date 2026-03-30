from django.contrib import admin
from .models import CourseCategory, Course, CourseVideo


class CourseVideoInline(admin.TabularInline):
    """
    Shows videos directly inside Course admin page.
    Admin can add multiple videos without going to a separate page.
    extra=3 means 3 empty rows shown by default.
    """
    model = CourseVideo
    extra = 3
    fields = ['title', 'youtube_url', 'duration', 'order']


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty_level', 'total_videos', 'is_active', 'created_at']
    list_filter = ['category', 'difficulty_level', 'is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseVideoInline]


@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'duration']
    list_filter = ['course']
