#!/usr/bin/env python

import logging
import os
import sys
import django

sys.path.append(".")
os.environ["DJANGO_SETTINGS_MODULE"] = "docrepo.settings"

django.setup()

from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from repo.models import Folder, Profile
from repo.model_utils import (
    create_user_home_folder,
    get_admin_user,
    get_home_folder,
    get_projects_folder,
    get_root_folder,
)
from repo.settings import (
    ROOT_FOLDER_NAME,
    HOME_FOLDER_NAME,
    PROJECT_FOLDER_NAME,
    ADMIN_USERNAME,
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
)


users = [
    {
        "username": "testuser1",
        "email": "testuser1@localhost",
        "password": "S3cr3t",
    }
]

ADD_DEMOS = True


LOGGER = logging.getLogger(__name__)


def create_user(admin_username, admin_email, admin_password):
    admin_user = User()
    admin_user.username = ADMIN_USERNAME
    admin_user.email = ADMIN_EMAIL
    admin_user.set_password(ADMIN_PASSWORD)
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    return admin_user


def create_admin_user():
    try:
        admin_user = User.objects.get(username=ADMIN_USERNAME)
    except:
        admin_user = create_user(
            admin_username=ADMIN_USERNAME,
            admin_email=ADMIN_EMAIL,
            admin_password=ADMIN_PASSWORD,
        )
    return admin_user


def create_root_folder(admin_user):
    LOGGER = logging
    LOGGER.info("Creating ROOT folder ...")
    try:
        root_folder = Folder.objects.get(name=ROOT_FOLDER_NAME, parent=None)
        LOGGER.info("  Root folder is already created.")
        LOGGER.warning("ROOT folder already created. Skipping.")
    except Folder.DoesNotExist:
        root_folder = Folder()
        root_folder.name = ROOT_FOLDER_NAME
        root_folder.title = "ROOT Folder"
        root_folder.description = "System Root Folder"
        root_folder.owner = admin_user
        root_folder.is_system = True
        root_folder.save()
        LOGGER.info("  Root folder is created.")
        LOGGER.info("  Done.")
    return root_folder


def create_home_folder(admin_user, root_folder):
    try:
        home_folder = Folder.objects.get(name=HOME_FOLDER_NAME, parent=root_folder)
        LOGGER.info("  Home folder is already created.")
    except Folder.DoesNotExist:
        home_folder = Folder()
        home_folder.name = HOME_FOLDER_NAME
        home_folder.title = "Home Folder"
        home_folder.description = "System Home Folder"
        home_folder.owner = admin_user
        home_folder.parent = root_folder
        home_folder.is_system = True
        home_folder.save()
        admin_user.profile.home_folder = home_folder
        admin_user.profile.save()
        LOGGER.info("  Home folder is created.")
    return home_folder


def create_project_folder(admin_user, root_folder):
    try:
        project_folder = Folder.objects.get(
            name=PROJECT_FOLDER_NAME, parent=root_folder
        )
        LOGGER.info("  Project folder is already created.")
    except Folder.DoesNotExist:
        project_folder = Folder()
        project_folder.name = PROJECT_FOLDER_NAME
        project_folder.title = "Projects Folder"
        project_folder.description = "System Projects Folder"
        project_folder.owner = admin_user
        project_folder.parent = root_folder
        project_folder.is_system = True
        project_folder.save()
        LOGGER.info("  Projects folder is created.")
    return project_folder


def create_users():
    for user in users:
        u = User()
        u.username = user["username"]
        u.email = user["email"]
        try:
            u.save()
            u.set_password(user["password"])
            u.save()
        except IntegrityError:
            LOGGER.info("  User: {} already created.".format(user["username"]))


def sys_check():
    checks = (get_root_folder, get_home_folder, get_projects_folder, get_admin_user)
    for checked in checks:
        if not checked():
            sys.stderr.write("{} fails. This must be fixed.")
            return False
    LOGGER.info("All tests passed.")
    return True


def create_admin_home_folder(admin_user):
    try:
        create_user_home_folder(
            admin_user, get_home_folder(), Profile.objects.get(user=admin_user)
        )
    except IntegrityError:
        pass


def main():
    LOGGER.info("Running initdata script ...")
    admin_user = create_admin_user()
    root_folder = create_root_folder(admin_user)
    create_home_folder(admin_user, root_folder)
    create_project_folder(admin_user, root_folder)
    create_admin_home_folder(admin_user)
    create_users()
    # sys_check()

    if ADD_DEMOS:
        from demos.phoenix_project.loader import PhoenixProjectLoader

        loader = PhoenixProjectLoader()
        loader.run()

        from demos.sample_folders_docs.loader import FolderDocsLoader

        loader = FolderDocsLoader()
        loader.run()

    LOGGER.info("  Done.")


if __name__ == "__main__":
    main()
