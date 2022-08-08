from repo.abstract_models import Timestampable, UUIDFieldModel
from django.db import models
from repo.models.content import ContentFile


class ContentFileIndex(UUIDFieldModel, Timestampable):
    content_file = models.ForeignKey(ContentFile, on_delete=models.CASCADE)
    text = models.TextField()

    class Meta:
        verbose_name = "ContentFile Index"
        verbose_name_plural = "ContentFile Indexes"

    def __str__(self):
        return "{}:{}".format(self.content_file.parent, self.content_file.version)
