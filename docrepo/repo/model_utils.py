import logging
import re
from django.contrib.auth.models import User

import repo.models
from .settings import (
    ROOT_FOLDER_NAME,
    HOME_FOLDER_NAME,
    PROJECT_FOLDER_NAME,
    ADMIN_USERNAME,
    ADMIN_EMAIL,
)

LOGGER = logging.getLogger(__name__)


def get_admin_user():
    """Admin user should be the only user with username as ADMIN_USERNAME, email is ADMIN_EMAIL, is_staff==True, is_superuser==True"""
    return User.objects.get(
        username=ADMIN_USERNAME, email=ADMIN_EMAIL, is_staff=True, is_superuser=True
    )


def get_root_folder():
    """System root folder should be the only folder with ROOT_FOLDER_NAME as name and with no parent folder."""
    return repo.models.Folder.objects.get(name=ROOT_FOLDER_NAME, parent=None)


def get_home_folder():
    """System home folder should be the only folder with HOME_FOLDER_NAME as name and root_folder as parent."""
    return repo.models.Folder.objects.get(
        name=HOME_FOLDER_NAME, parent=get_root_folder()
    )


def get_projects_folder():
    """Projects folder should be the only folder with PROJECT_FOLDER_NAME as name and root_folder as parent."""
    return repo.models.Folder.objects.get(
        name=PROJECT_FOLDER_NAME, parent=get_root_folder()
    )


def set_profile_home_folder(profile, home_folder, trashcan_folder):
    LOGGER.debug("Retrieved profile: {}".format(profile))
    LOGGER.debug("Home folder for {} is {}".format(profile, home_folder))
    LOGGER.debug("Trashcan folder is {}".format(trashcan_folder))
    profile.home_folder = home_folder
    profile.trashcan_folder = trashcan_folder
    profile.save()
    LOGGER.debug("SAVED PROFILE IS: {}".format(profile))
    LOGGER.debug(
        "Home folder for {} has been set to {}".format(profile, profile.home_folder)
    )


def create_project_home_folder(instance):
    return repo.overflow_models.containers.Folder.objects.create(
        name=instance.name, owner=instance.owner, parent=get_projects_folder()
    )


def create_trashcan_folder(user, home_folder=None):
    if not home_folder:
        home_folder = user.profile.home_folder
    trashcan_folder = repo.overflow_models.containers.Folder()
    trashcan_folder.name = "Trashcan"
    trashcan_folder.parent = home_folder
    trashcan_folder.owner = user
    trashcan_folder.title = "Trashcan folder for {}".format(user.username)
    trashcan_folder.description = "System trashcan folder for {}".format(user.username)
    trashcan_folder.is_system = True
    trashcan_folder.save()
    LOGGER.debug("Created the trashcan folder and attaching it to the user's profile.")
    user.profile.trashcan_folder = trashcan_folder
    user.profile.save()
    return trashcan_folder


def add_home_folder(user, sys_home_folder):
    home_folder = repo.overflow_models.containers.Folder()
    home_folder.name = user.username
    home_folder.parent = sys_home_folder
    home_folder.owner = user
    home_folder.title = "Home folder for {}".format(user.username)
    home_folder.description = "System user home folder for {}".format(user.username)
    home_folder.is_system = True
    home_folder.save()
    return home_folder


def create_user_home_folder(user, sys_home_folder, profile=None):
    home_folder = add_home_folder(user, sys_home_folder)
    trashcan_folder = create_trashcan_folder(user, home_folder)
    set_profile_home_folder(profile, home_folder, trashcan_folder)


def get_cleaned_project_name(instance):
    cleaned_proj_name = instance.name.lower().replace(" ", "_")
    cleaned_proj_name = re.sub("[^a-zA-Z0-9 \n\.]", "_", cleaned_proj_name)
    return cleaned_proj_name
