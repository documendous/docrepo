from django.db import models

import repo
from repo.abstract_models import Timestampable, UUIDFieldModel


class PreviewFile(UUIDFieldModel, Timestampable):
    file = models.FileField(upload_to="%Y/%m/%d/%H/%M/")
    parent = models.ForeignKey(
        repo.overflow_models.content.ContentFile, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Preview File"
        verbose_name_plural = "Preview Files"
        ordering = ["file"]

    def __str__(self):
        return "{}:{}".format(self.parent, self.file.file)
