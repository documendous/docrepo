from copy import deepcopy
from itertools import chain
import logging
import os
import pathlib
import time
import uuid
from django.contrib.auth.models import User
from django.core.files import File
from django.db import IntegrityError
from docrepo.settings import MEDIA_ROOT
from repo.model_utils import get_cleaned_project_name, get_home_folder

from repo.overflow_models.containers import Folder
from repo.overflow_models.content import ContentFile, Document
from repo.overflow_models.projects import Project
from repo.settings import ADMIN_USERNAME, DEFAULT_DOC_VERSION


def get_model_list(parent_folder, user):
    LOGGER = logging.getLogger(__name__)
    LOGGER.debug("Calling get_model_list")
    model_list = list(
        chain(
            Folder.objects.filter(parent=parent_folder)
            .order_by("name")
            .exclude(name="Trashcan", parent__parent=get_home_folder()),
            Document.objects.filter(parent=parent_folder).order_by("name"),
        )
    )
    results = private_site_folders_removed(model_list, user)
    LOGGER.debug("Results are: {}".format(results))
    return results


def in_project_path(parent_folder):
    if parent_folder:
        results = parent_folder.is_in_project()
    else:
        results = None
    if results:
        is_in_project = results["?"]
        project = results["project"]
    else:
        is_in_project = False
        project = None
    return is_in_project, project


def private_site_folders_removed(model_list, user):
    LOGGER = logging.getLogger(__name__)
    if user.username == ADMIN_USERNAME:
        """The admin user can see all projects."""
        return model_list

    excepted_private_project_folders = []
    for item in model_list:
        if item.type() == "folder":
            result = item.is_project_folder()
            LOGGER.debug(
                "Result: is_project? {}; project? {}".format(
                    result["?"], result["project"]
                )
            )
            if result["?"]:
                project = result["project"]
                if user in project.members.all():
                    excepted_private_project_folders.append(item)

    for item in model_list:
        if item.id in Project.objects.filter(access="private").exclude(
            owner=user
        ).values_list("home_folder", flat=True):
            model_list.remove(item)

    LOGGER.debug("Model list type is {}".format(type(model_list)))
    LOGGER.debug(
        "Excepted Private Project Folders type is {}".format(
            type(excepted_private_project_folders)
        )
    )
    for item in excepted_private_project_folders:
        if item not in model_list:
            LOGGER.debug("Item type is {}".format(type(item)))
            model_list.append(item)

    return model_list


def is_project_member(project, request):
    if project:
        if request.user in project.members.all():
            return True
        return False
    return False


def checked_project_privileges(request, container):
    LOGGER = logging.getLogger(__name__)
    user_is_consumer = False
    user_is_editor = False
    user_is_contributor = False
    user_is_manager = False
    project_access = None

    is_in_project, project = in_project_path(parent_folder=container)
    is_member = is_project_member(project, request)
    LOGGER.debug("Container in project: {}, project: {}".format(is_in_project, project))
    if is_in_project and project:
        LOGGER.debug("Type of project is {}".format(type(project)))
        if request.user in project.members.all():
            LOGGER.debug("User is in project memebership list.")
            group_memberships = request.user.groups.values_list("name", flat=True)
            LOGGER.debug(
                "User: {} group memberships are: {}".format(
                    request.user, group_memberships
                )
            )
            for membership in group_memberships:
                LOGGER.debug("  Group membership: {}".format(membership))
                LOGGER.debug("  type of member: {}".format(type(membership)))
                LOGGER.debug(
                    "  checking '{}-consumers' in membership: {}".format(
                        project, membership
                    )
                )
                if (
                    "{}-consumers".format(get_cleaned_project_name(project))
                    in membership
                ):
                    user_is_consumer = True

                LOGGER.debug(
                    "  checking '{}-editors' in membership: {}".format(
                        project, membership
                    )
                )
                if "{}-editors".format(get_cleaned_project_name(project)) in membership:
                    user_is_editor = True

                LOGGER.debug(
                    "  checking '{}-contributors' in membership: {}".format(
                        project, membership
                    )
                )
                if (
                    "{}-contributors".format(get_cleaned_project_name(project))
                    in membership
                ):
                    user_is_contributor = True

                LOGGER.debug(
                    "  checking '{}-managers' in membership: {}".format(
                        project, membership
                    )
                )
                if (
                    "{}-managers".format(get_cleaned_project_name(project))
                    in membership
                ):
                    user_is_manager = True
        else:
            LOGGER.debug("User is not showing in project membership list.")

        if container.is_open_project():
            project_access = "open"

    results = (
        user_is_consumer,
        user_is_editor,
        user_is_contributor,
        user_is_manager,
        is_in_project,
        project,
        is_member,
        project_access,
    )
    LOGGER.debug(
        "    Results are: user_is_consumer: {}, user_is_contributor: {}, user_is_editor: {}, user_is_manager: {} is_member: {}".format(
            user_is_consumer,
            user_is_contributor,
            user_is_editor,
            user_is_manager,
            is_member,
        )
    )
    return results


def create_content_file(uploaded_file, document):
    LOGGER = logging.getLogger(__name__)
    temp_file_name = "{}/tmp/{}".format(MEDIA_ROOT, uploaded_file)
    LOGGER.debug("Attempting to write uploaded file to: {}".format(temp_file_name))

    destination = open(temp_file_name, "wb+")
    for chunk in uploaded_file.chunks():
        destination.write(chunk)
    destination.close()

    local_file = open(temp_file_name, "rb")
    djangofile = File(local_file)
    content_file = ContentFile()
    LOGGER.debug("ContentFile will be: {}".format(djangofile))
    content_file.parent = document
    content_file.file.save(str(uuid.uuid4()) + ".bin", djangofile)
    content_file.save()
    local_file.close()
    document.content_files.add(content_file)
    document.save()
    try:
        os.remove(temp_file_name)
        LOGGER.debug("  Removed temp file: {}".format(temp_file_name))
    except Exception as err:
        LOGGER.error("Unable to remove temp file: {}".format(temp_file_name))
        LOGGER.error(repr(err))


def recycle_document(document, profile):
    orig_name = document.name
    orig_container = document.parent
    document.parent = profile.trashcan_folder
    document.orig_parent = orig_container
    document.orig_name = orig_name
    base_name = pathlib.Path(document.name).stem
    extension = os.path.splitext(document.name)[-1]
    document.name = "{}-{}{}".format(base_name, time.time(), extension)
    document.save()
    return orig_container


def recycle_folder(folder, profile):
    orig_container = folder.parent
    orig_name = folder.name
    folder.parent = profile.trashcan_folder
    folder.orig_parent = orig_container
    folder.orig_name = orig_name
    base_name = pathlib.Path(folder.name).stem
    extension = os.path.splitext(folder.name)[-1]
    folder.name = "{}-{}{}".format(base_name, time.time(), extension)
    folder.save()
    return orig_container


def get_new_version(content_file, version_type):
    parent_document = content_file.parent
    existing_versions = ContentFile.objects.filter(parent=parent_document)
    if len(existing_versions) > 0:
        latest_version = parent_document.get_latest_version()
        major, minor = latest_version.split(".")
        if version_type == "major":
            major = int(major) + 1
            minor = 0
        elif version_type == "minor":
            minor = int(minor) + 1
        else:
            raise ValueError(
                "version_type: {} is an invalid version_type.".format(version_type)
            )
        new_version = "{}.{}".format(major, minor)
        return new_version
    else:
        return DEFAULT_DOC_VERSION


def copy_document(document, destination_folder, request):
    LOGGER = logging.getLogger(__name__)
    copy_document = deepcopy(document)
    copy_document.id = uuid.uuid4()
    copy_document.parent = destination_folder
    copy_document.owner = request.user

    try:
        copy_document.save()
    except IntegrityError as err:
        LOGGER.warn(repr(err))
        return None

    copy_file = deepcopy(
        ContentFile.objects.get(parent=document, version=document.get_latest_version())
    )
    copy_file.id = uuid.uuid4()
    copy_file.parent = copy_document
    copy_file.save()
    copy_document.content_files.add(copy_file)
    copy_document.save()
    return copy_document


def copy_folder(folder, destination_folder, request):
    LOGGER = logging.getLogger(__name__)
    the_copy_folder = deepcopy(folder)
    the_copy_folder.id = uuid.uuid4()
    the_copy_folder.parent = destination_folder
    the_copy_folder.owner = request.user

    try:
        the_copy_folder.save()
    except IntegrityError as err:
        LOGGER.warn(repr(err))
        return None

    the_copy_folder.save()

    LOGGER.debug(
        "Copied folder is {} with children: {}".format(folder, folder.children())
    )

    for model in folder.children():
        LOGGER.debug("Model type is: {}".format(model.type()))
        if model.type() == "document":
            LOGGER.debug(
                "Calling copy_document with: {} and {}".format(model, the_copy_folder)
            )
            copy_document(
                document=model, destination_folder=the_copy_folder, request=request
            )
        elif model.type() == "folder":
            LOGGER.debug(
                "Recursive call to this function with: {} and {}".format(
                    model, the_copy_folder
                )
            )
            copy_folder(
                folder=model, destination_folder=the_copy_folder, request=request
            )

    return the_copy_folder


def set_group_assignments(project, managers, contributors, editors, consumers):
    LOGGER = logging.getLogger(__name__)
    LOGGER.debug("Managers: {}".format(managers))
    for user_id in managers:
        user = User.objects.get(pk=user_id)
        LOGGER.debug(
            "Assigning {}/{} to group {}".format(
                user_id, user.username, project.manager_group
            )
        )
        user.groups.add(project.manager_group)
        user.groups.remove(project.contributor_group)
        user.groups.remove(project.editor_group)
        user.groups.remove(project.consumer_group)
        user.save()

    LOGGER.debug("Contributors: {}".format(contributors))
    for user_id in contributors:
        user = User.objects.get(pk=user_id)
        LOGGER.debug(
            "Assigning {}/{} to group {}".format(
                user_id, user.username, project.contributor_group
            )
        )
        user.groups.add(project.contributor_group)
        user.groups.remove(project.manager_group)
        user.groups.remove(project.editor_group)
        user.groups.remove(project.consumer_group)
        user.save()

    LOGGER.debug("Editors: {}".format(editors))
    for user_id in editors:
        user = User.objects.get(pk=user_id)
        LOGGER.debug(
            "Assigning {}/{} to group {}".format(
                user_id, user.username, project.editor_group
            )
        )
        user.groups.add(project.editor_group)
        user.groups.remove(project.manager_group)
        user.groups.remove(project.contributor_group)
        user.groups.remove(project.consumer_group)
        user.save()

    LOGGER.debug("Consumers: {}".format(consumers))
    for user_id in consumers:
        user = User.objects.get(pk=user_id)
        LOGGER.debug(
            "Assigning {}/{} to group {}".format(
                user_id, user.username, project.consumer_group
            )
        )
        user.groups.add(project.consumer_group)
        user.groups.remove(project.manager_group)
        user.groups.remove(project.contributor_group)
        user.groups.remove(project.editor_group)
        user.save()


def get_project_role(user, project):
    LOGGER = logging.getLogger(__name__)
    roles = []
    if project and user:
        LOGGER.debug(
            "Checking for role for user: {} in project: {}".format(user, project)
        )

        if project.owner == user:
            roles.append("Owner")

        user_groups = user.groups.all()

        for group in user_groups:
            if group == project.consumer_group:
                roles.append("Consumer")
            elif group == project.editor_group:
                roles.append("Editor")
            elif group == project.contributor_group:
                roles.append("Contributor")
            elif group == project.manager_group:
                roles.append("Manager")

    if not roles:
        roles.append("None Assigned")

    return ", ".join(roles)


def get_model_ids_parents(model_ids: str):
    LOGGER = logging.getLogger(__name__)
    model_ids = model_ids.split(",")
    parents = []
    for each in model_ids:
        try:
            parents.append(Document.objects.get(pk=each).parent)
        except Document.DoesNotExist as doc_err:
            try:
                parents.append(Folder.objects.get(pk=each).parent)
            except Folder.DoesNotExist as folder_err:
                LOGGER.error(repr(doc_err))
                LOGGER.error(repr(folder_err))

    return parents
