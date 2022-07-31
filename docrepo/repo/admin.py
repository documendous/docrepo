from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.sites import AlreadyRegistered
from django.apps import apps
from .models import (
    ContentFile,
    Document,
    Folder,
    Organization,
    OrphanContent,
    Profile,
    Project,
)


class ContentFileAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


class FolderAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


class OrphanContentAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


class OrganizationAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ("id",)


# model registered with custom admin
admin.site.register(ContentFile, ContentFileAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(OrphanContent, OrphanContentAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        ...
