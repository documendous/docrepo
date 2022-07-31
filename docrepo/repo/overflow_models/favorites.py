from django.db import models
from repo.overflow_models.containers import Folder
from repo.overflow_models.content import Document
from repo.abstract_models import Favorite


class FavoriteDocument(Favorite):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("document", "profile"),)
        verbose_name = "Favorite Document"
        verbose_name_plural = "Favorite Documents"
        ordering = ["profile"]

    def __str__(self):
        return "{} / {}".format(self.document.path(), self.profile.user.username)


class FavoriteFolder(Favorite):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("folder", "profile"),)
        verbose_name = "Favorite Folder"
        verbose_name_plural = "Favorite Folders"
        ordering = ["profile"]

    def __str__(self):
        return "{} / {}".format(self.folder.path(), self.profile.user.username)
