import logging
import os
import uuid
from django.db import IntegrityError
from django.shortcuts import render
from django.views import View

from repo.models.utils import get_home_folder, get_projects_folder
from repo.models.containers import Folder
from repo.models.content import Document
from repo.models.people import Profile
from repo.constants import ADMIN_USERNAME
from ui.views.utils import (
    checked_project_privileges,
    copy_document,
    copy_folder,
    get_model_ids_parents,
    recycle_document,
    recycle_folder,
)


def get_valid_container_children(container, model_ids):
    container_children = []
    for item in container.child_folders():
        if str(item.id) not in model_ids:
            container_children.append(item)
    return container_children


class CopyModelsView(View):
    def get(self, request, model_ids, folder_id):
        model_ids = model_ids
        container = Folder.objects.get(pk=folder_id)
        model_ids_parents = get_model_ids_parents(model_ids)
        return render(
            request,
            "ui/select-folders.html",
            {
                "model_ids": model_ids,
                "container": container,
                "select_view": "ui-folder-select-forcopy-view",
                "admin_username": ADMIN_USERNAME,
                "container_children": get_valid_container_children(
                    container, model_ids
                ),
                "projects_folder": get_projects_folder(),
                "system_home_folder": get_home_folder(),
                "model_ids_parents": model_ids_parents,
            },
        )

    def post(self, request, model_ids, folder_id):
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug("Calling CopyModelsView.post")
        model_ids = model_ids.split(",")
        container = Folder.objects.get(pk=folder_id)
        destination_folder = None
        if request.POST.get("destination_folder"):
            destination_folder = Folder.objects.get(
                pk=request.POST.get("destination_folder")
            )

            LOGGER.debug("Checking user's project permissions.")
            (
                user_is_consumer,
                user_is_editor,
                user_is_contributor,
                user_is_manager,
                is_in_project,
                project,
                is_member,
                project_access,
            ) = checked_project_privileges(request, destination_folder)

            for model_id in model_ids:
                document = None
                folder = None
                try:
                    document = Document.objects.get(pk=model_id)
                except Document.DoesNotExist as doc_err:
                    try:
                        folder = Folder.objects.get(pk=model_id)
                    except Folder.DoesNotExist as folder_err:
                        LOGGER.error(repr(doc_err))
                        LOGGER.error(repr(folder_err))
                if document:
                    LOGGER.debug(
                        "Going to copy a new document for {} and place it in the {} folder.".format(
                            document, destination_folder
                        )
                    )
                    if (
                        request.user.username == ADMIN_USERNAME
                        or document.owner == request.user
                        and destination_folder.owner == request.user
                        or user_is_contributor
                        and is_member
                        or user_is_manager
                        and is_member
                    ):
                        LOGGER.debug("Attempting deepcopy of {}".format(document))
                        copy_doc = copy_document(document, destination_folder, request)
                        if copy_doc:
                            LOGGER.debug("Deep copy successful: {}".format(copy_doc))
                        else:
                            LOGGER.warn(
                                "Something went wrong during copy of {} to {}".format(
                                    document, destination_folder
                                )
                            )

                elif folder:
                    LOGGER.debug(
                        "Going to copy a new folder and new contents for {} and place it in the {} folder.".format(
                            folder, destination_folder
                        )
                    )
                    if (
                        request.user.username == ADMIN_USERNAME
                        or folder.owner == request.user
                        and destination_folder.owner == request.user
                        or user_is_contributor
                        and is_member
                        or user_is_manager
                        and is_member
                    ):
                        LOGGER.debug(
                            "Attempting deepcopy of {} and its contents.".format(folder)
                        )
                        copy_f = copy_folder(folder, destination_folder, request)
                        if copy_f:
                            LOGGER.debug("Deep copy successful: {}".format(copy_f))
                        else:
                            LOGGER.warn(
                                "Something went wrong during copy of {} to {}".format(
                                    folder, destination_folder
                                )
                            )
                    else:
                        LOGGER.error(
                            "Unauthorized to move folder: {} to destination folder: {}".format(
                                folder, destination_folder
                            )
                        )

        return render(request, "ui/close-this.html", {})


class MoveModelsView(View):
    def get(self, request, model_ids, folder_id):
        model_ids = model_ids
        container = Folder.objects.get(pk=folder_id)
        model_ids_parents = get_model_ids_parents(model_ids)
        return render(
            request,
            "ui/select-folders.html",
            {
                "model_ids": model_ids,
                "container": container,
                "select_view": "ui-folder-select-formove-view",
                "admin_username": ADMIN_USERNAME,
                "container_children": get_valid_container_children(
                    container, model_ids
                ),
                "projects_folder": get_projects_folder(),
                "system_home_folder": get_home_folder(),
                "model_ids_parents": model_ids_parents,
            },
        )

    def post(self, request, model_ids, folder_id):
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug("Calling MoveModelsView.post")
        model_ids = model_ids.split(",")
        container = Folder.objects.get(pk=folder_id)
        destination_folder = None
        if request.POST.get("destination_folder"):
            destination_folder = Folder.objects.get(
                pk=request.POST.get("destination_folder")
            )

            LOGGER.debug("Checking user's project permissions.")
            (
                user_is_consumer,
                user_is_editor,
                user_is_contributor,
                user_is_manager,
                is_in_project,
                project,
                is_member,
                project_access,
            ) = checked_project_privileges(request, destination_folder)

            for model_id in model_ids:
                document = None
                folder = None
                try:
                    document = Document.objects.get(pk=model_id)
                except Document.DoesNotExist as doc_err:
                    try:
                        folder = Folder.objects.get(pk=model_id)
                    except Folder.DoesNotExist as folder_err:
                        LOGGER.error(repr(doc_err))
                        LOGGER.error(repr(folder_err))
                if document:
                    LOGGER.debug(
                        "Going to move document: {} and place it in the {} folder.".format(
                            document, destination_folder
                        )
                    )
                    if (
                        request.user.username == ADMIN_USERNAME
                        or document.owner == request.user
                        and destination_folder.owner == request.user
                        or user_is_contributor
                        and is_member
                        or user_is_manager
                        and is_member
                    ):
                        document.parent = destination_folder
                        try:
                            document.save()
                        except IntegrityError:
                            name, ext = os.path.splitext(document.name)
                            document.name = name + "-" + str(document.id) + ext
                            document.save()
                    else:
                        LOGGER.error(
                            "Unauthorized to move document: {} to destination folder: {}".format(
                                document, destination_folder
                            )
                        )

                elif folder:
                    LOGGER.debug(
                        "Going to move folder and contents: {} and place it in the {} folder.".format(
                            folder, destination_folder
                        )
                    )
                    if (
                        request.user.username == ADMIN_USERNAME
                        or folder.owner == request.user
                        and destination_folder.owner == request.user
                        or user_is_contributor
                        and is_member
                        or user_is_manager
                        and is_member
                    ):
                        folder.parent = destination_folder
                        try:
                            folder.save()
                        except IntegrityError:
                            name, ext = os.path.splitext(folder.name)
                            folder.name = name + "-" + str(folder.id) + ext
                            folder.save()
                    else:
                        LOGGER.error(
                            "Unauthorized to move folder: {} to destination folder: {}".format(
                                document, destination_folder
                            )
                        )

        return render(request, "ui/close-this.html", {})


class BulkRecycleView(View):
    def get(self, request, model_ids, profile_id):
        LOGGER = logging.getLogger(__name__)
        model_ids = model_ids.split(",")
        document_list = []
        folder_list = []

        for model_id in model_ids:
            try:
                document = Document.objects.get(pk=model_id)
                document_list.append(document)
            except Document.DoesNotExist as doc_err:
                try:
                    folder = Folder.objects.get(pk=model_id)
                    folder_list.append(folder)
                except Folder.DoesNotExist as folder_err:
                    LOGGER.warn(repr(doc_err))
                    LOGGER.warn(repr(folder_err))

        profile = Profile.objects.get(pk=profile_id)
        return render(
            request,
            "ui/bulk-recycle.html",
            {
                "model_ids": model_ids,
                "profile": profile,
                "document_list": document_list,
                "folder_list": folder_list,
            },
        )

    def post(self, request, model_ids, profile_id):
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug("Calling BulkRecycleView.post")
        model_ids = model_ids.split(",")
        profile = Profile.objects.get(pk=profile_id)

        document_list = []
        folder_list = []

        for model_id in model_ids:
            try:
                document = Document.objects.get(pk=model_id)
                document_list.append(document)
            except Document.DoesNotExist as doc_err:
                try:
                    folder = Folder.objects.get(pk=model_id)
                    folder_list.append(folder)
                except Folder.DoesNotExist as folder_err:
                    LOGGER.warn(repr(doc_err))
                    LOGGER.warn(repr(folder_err))

        for document in document_list:
            LOGGER.debug("Recycling document: {}".format(document))
            recycle_document(document, profile)

        for folder in folder_list:
            LOGGER.debug("Recycling folder: {} and contents.".format(folder))
            recycle_folder(folder, profile)

        return render(request, "ui/close-this.html", {})
