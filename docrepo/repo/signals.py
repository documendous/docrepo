import logging
import os
import magic
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.contrib.auth.models import User, Group
from repo.models.content import ContentType
from .models.utils import (
    create_project_home_folder,
    create_user_home_folder,
    get_cleaned_project_name,
)
from repo.models.content import (
    Document,
    OrphanContent,
    ContentFile,
)
from repo.models.people import Profile
from repo.models.projects import Project
from repo.models.containers import Folder
from .settings import (
    AUTO_DELETE_CONTENT_FILES,
)
from .constants import HOME_FOLDER_NAME, ROOT_FOLDER_NAME, ADMIN_USERNAME
from docrepo.settings import (
    BASE_DIR,
)


@receiver(post_save, sender=Folder)
def check_root_exists_on_save(sender, instance, created, **kwargs):
    # https://medium.com/@singhgautam7/django-signals-master-pre-save-and-post-save-422889b2839
    if created:
        root_folders = Folder.objects.filter(name=ROOT_FOLDER_NAME, parent=None)
        if root_folders.count() > 1:
            instance.delete()


@receiver(post_save, sender=Document)
def create_document(sender, instance, created, **kwargs):
    if created:
        document = instance
        document.extension = document.get_extension()
        document.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        if instance.username != ADMIN_USERNAME:
            root_folder = Folder.objects.get(name=ROOT_FOLDER_NAME, parent=None)
            sys_home_folder = Folder.objects.get(
                name=HOME_FOLDER_NAME, parent=root_folder
            )
            create_user_home_folder(instance, sys_home_folder, profile=profile)
        else:
            pass


@receiver(post_save, sender=ContentFile)
def set_contenttype(sender, instance, created, **kwargs):
    LOGGER = logging.getLogger(__name__)
    if created:
        LOGGER.debug("Instance is {} and type: {}".format(instance, type(instance)))
        details = magic.from_file(str(BASE_DIR / "contentfiles" / str(instance.file)))
        LOGGER.debug("Details for {}: {}".format(instance, details))
        try:
            content_type, version = details.split(", ")
            LOGGER.debug("ContentType version: {}".format(version))
        except ValueError:
            content_type = details
            version = None
        LOGGER.debug("Mimetype: {}".format(content_type))

        if content_type:
            try:
                LOGGER.debug("Content type name is {}".format(content_type))
                ct = ContentType.objects.get(name=content_type)
            except ContentType.DoesNotExist:
                ct = ContentType()
                ct.name = content_type
                if version:
                    ct.version = version
                ct.save()

            document = instance.parent
            document.content_type = ct
            document.save()


@receiver(post_delete, sender=ContentFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    LOGGER = logging.getLogger(__name__)
    if AUTO_DELETE_CONTENT_FILES:
        LOGGER.debug("  AUTO_DELETE_CONTENT_FILES is set to True")
        if instance.file:
            if os.path.isfile(instance.file.path):
                LOGGER.debug(
                    "  Deleting ContentFile: {} from file system".format(
                        instance.file.path
                    )
                )
                os.remove(instance.file.path)
            else:
                LOGGER.warn(
                    "  ContentFile: {} does not exist and cannot be deleted.".format(
                        instance.file.path
                    )
                )
    else:
        orphan = OrphanContent()
        orphan.orig_parent_type = "content_file"
        orphan.orig_parent_path = instance.parent.get_path()
        orphan.content_file_path = instance.file.path
        orphan.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Project)
def create_project_folder(sender, instance, created, **kwargs):
    if created:
        cleaned_proj_name = get_cleaned_project_name(instance)

        instance.home_folder = create_project_home_folder(instance)

        instance.manager_group = Group.objects.create(
            name="{}-managers".format(cleaned_proj_name)
        )

        instance.contributor_group = Group.objects.create(
            name="{}-contributors".format(cleaned_proj_name)
        )

        instance.editor_group = Group.objects.create(
            name="{}-editors".format(cleaned_proj_name)
        )

        instance.consumer_group = Group.objects.create(
            name="{}-consumers".format(cleaned_proj_name)
        )

        instance.save()


@receiver(m2m_changed, sender=Project.members.through)
def membership_changed(sender, **kwargs):
    LOGGER = logging.getLogger(__name__)
    instance = kwargs.pop("instance", None)
    pk_set = kwargs.pop("pk_set", None)
    action = kwargs.pop("action", None)
    project = instance

    if action == "post_remove":
        LOGGER.debug("Post remove for project membership fired.")
        LOGGER.debug("Instance is {}".format(instance))
        LOGGER.debug("pk_set is {}".format(pk_set))
        for each in pk_set:
            user = User.objects.get(pk=each)
            user.groups.remove(project.manager_group)
            user.groups.remove(project.contributor_group)
            user.groups.remove(project.editor_group)
            user.groups.remove(project.consumer_group)
            user.save()
