from django.contrib import admin
from .models import Category, Project, ProjectImage, ProjectDownload


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]


admin.site.register(Category)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectDownload)