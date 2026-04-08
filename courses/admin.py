from django.contrib import admin
from .models import CourseCategory, Course, CourseVideo


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


class CourseVideoInline(admin.TabularInline):
    """
    Shows videos inside the Course admin page.
    Admin can add/edit videos directly from the course detail page.
    """
    model = CourseVideo
    extra = 1
    fields = ('order', 'title', 'youtube_url', 'duration', 'notes')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty_level',
                    'is_active', 'total_videos', 'created_at')
    list_filter = ('category', 'difficulty_level', 'is_active')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CourseVideoInline]


@admin.register(CourseVideo)
class CourseVideoAdmin(admin.ModelAdmin):
    """
    Separate admin page for CourseVideo.
    Admin can open any video and paste full HTML notes in the notes textarea.
    """
    list_display = ('title', 'course', 'order', 'duration', 'has_notes')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    ordering = ('course', 'order')

    # notes field will appear as a large textarea in the admin form
    fields = ('course', 'order', 'title', 'youtube_url', 'duration', 'notes')

    def has_notes(self, obj):
        """Shows YES/NO in the list view so admin knows which videos have notes."""
        return bool(obj.notes)
    has_notes.boolean = True
    has_notes.short_description = 'Notes Added?'
