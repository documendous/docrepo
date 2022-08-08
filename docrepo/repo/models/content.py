import os
from django.db import models
from repo.models.containers import Folder
from repo.settings import DEFAULT_DOC_VERSION
from repo.abstract_models import (
    BaseDublinCore,
    Ownable,
    Timestampable,
    UUIDFieldModel,
    UUIDNamedFileField,
)


class ContentType(models.Model):
    name = models.TextField(unique=True)
    version = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = (("name", "version"),)
        verbose_name = "Content Type"
        verbose_name_plural = "Content Types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ContentFile(UUIDFieldModel, Timestampable):
    file = UUIDNamedFileField(upload_to="%Y/%m/%d/%H/%M/", max_length=260)
    version = models.CharField(max_length=12, default=DEFAULT_DOC_VERSION)
    parent = models.ForeignKey("Document", on_delete=models.CASCADE)
    is_indexed = models.BooleanField(default=False)
    index_error = models.TextField(null=True, blank=True)
    is_acknowledged = models.BooleanField(default=False)
    version_type = models.CharField(
        "Version Type",
        max_length=30,
        choices=(("major", "major"), ("minor", "minor")),
        default="minor",
    )

    class Meta:
        unique_together = (("file", "version", "parent"),)
        verbose_name = "Content File"
        verbose_name_plural = "Content Files"
        ordering = ["parent__name"]

    def __str__(self):
        return "{}:{}".format(self.parent, self.version)


class Document(BaseDublinCore, UUIDFieldModel, Ownable, Timestampable):
    content_files = models.ManyToManyField(ContentFile, blank=True)
    extension = models.CharField(max_length=20, null=True, blank=True)
    parent = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="document_parent"
    )
    orig_parent = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="document_orig_parent",
    )
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        unique_together = (("name", "parent"),)
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["name"]

    def _build_path(self):
        """Recursive method to build the path based on having a parent"""
        if not self.parent:
            return f"/{self.name}/"
        else:
            return f"{self.parent._build_path()}{self.name}/"

    def _cleaned_path(self, path):
        """Clean path of any unnecessary pieces"""
        return path.rstrip("/")

    def get_path(self):
        """Gets a built path and cleans it up before returning"""
        return self._cleaned_path(self._build_path())

    def path(self):
        return self.get_path()

    def type(self):
        return "document"

    def get_extension(self):
        extension = os.path.splitext(self.name)[-1]
        return extension

    def size(self):
        latest_version = self.content_files.all()[0]
        return latest_version.file.size

    def get_latest_version(self):
        content_files = ContentFile.objects.filter(parent=self).order_by("-added")
        latest_version = content_files[0].version
        return latest_version

    def latest_version(self):
        return ContentFile.objects.filter(parent=self).order_by("-added")[0]

    def is_in_project(self):
        if self.parent:
            results = self.parent.is_in_project()
            if results["?"]:
                return results
            else:
                return results
        else:
            return {"?": False, "project": None}

    def __str__(self):
        return self.get_path()


class OrphanContent(UUIDFieldModel, Timestampable):
    content_file_path = models.CharField(max_length=255)
    orig_parent_type = models.CharField(
        max_length=30,
        choices=(
            ("content_file", "content_file"),
            ("preview_file", "preview_file"),
        ),
    )
    orig_parent_path = models.TextField()

    class Meta:
        verbose_name = "Orphan Content File"
        verbose_name_plural = "Orphan Content Files"

    def __str__(self):
        return "{}".format(self.content_file_path)
