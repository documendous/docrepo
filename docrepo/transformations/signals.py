import logging
import os
from django.dispatch import receiver
from django.db.models.signals import post_delete

from docrepo.repo.overflow_models.search import OrphanContent

from .models import (
    PreviewFile,
)
from .settings import (
    AUTO_DELETE_CONTENT_FILES,
)


LOGGER = logging.getLogger(__name__)


@receiver(post_delete, sender=PreviewFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if AUTO_DELETE_CONTENT_FILES:
        LOGGER.debug("  AUTO_DELETE_CONTENT_FILES is set to True")
        if instance.file:
            if os.path.isfile(instance.file.path):
                LOGGER.debug(
                    "  Deleting PreviewFile: {} from file system".format(
                        instance.file.path
                    )
                )
                os.remove(instance.file.path)
            else:
                LOGGER.warn(
                    "  PreviewFile: {} does not exist and cannot be deleted.".format(
                        instance.file.path
                    )
                )

    else:
        orphan = OrphanContent()
        orphan.orig_parent_type = "preview_file"
        orphan.orig_parent_path = instance.parent.parent.get_path()
        orphan.content_file_path = instance.file.path
        orphan.save()
