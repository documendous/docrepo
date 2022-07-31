from django.contrib import admin

from transformations.models import PreviewFile


class PreviewFileAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "added", "modified")


admin.site.unregister(PreviewFile)
admin.site.register(PreviewFile, PreviewFileAdmin)
