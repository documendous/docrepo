import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from repo.overflow_models.people import Profile
from repo.model_utils import (
    get_admin_user,
    get_home_folder,
    get_projects_folder,
    get_root_folder,
)
from repo.overflow_models.containers import Folder
from repo.settings import ADMIN_USERNAME, APP_NAME, FOOTER_TEXT
from ui.forms import AddFolderForm, UpdateFolderForm
from ui.views.utils import (
    checked_project_privileges,
    get_model_list,
    get_project_role,
    recycle_folder,
)


class FolderView(View):
    def get(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        container = Folder.objects.get(pk=folder_id)

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or container.owner == get_admin_user()
            and container.is_system
            and container != get_admin_user().profile.home_folder
            or user_is_consumer
            and is_member
            or user_is_editor
            and is_member
            or user_is_contributor
            and is_member
            or user_is_manager
            and is_member
            or project_access == "open"
        ):

            model_list = get_model_list(parent_folder=container, user=request.user)

            add_folder_form = AddFolderForm(
                initial={"parent": container, "owner": request.user}
            )

            LOGGER.debug(
                "User permissions for container: {}: user_is_consumer: {}, user_is_contributor: {}, user_is_editor: {}, user_is_manager: {}, project: {}".format(
                    container.get_path(),
                    user_is_consumer,
                    user_is_contributor,
                    user_is_editor,
                    user_is_manager,
                    project,
                )
            )

            project_role = get_project_role(user=request.user, project=project)

            return render(
                request,
                "ui/repository.html",
                {
                    "root_container": root_container,
                    "model_list": model_list,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "add_folder_form": add_folder_form,
                    "is_in_project": is_in_project,
                    "project": project,
                    "is_member": is_member,
                    "admin_username": ADMIN_USERNAME,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "show_modal": False,
                    "system_projects_folder": get_projects_folder(),
                    "system_home_folder": get_home_folder(),
                    "in_trashcan": container.in_trashcan(),
                    "project_access": project_access,
                    "project_role": project_role,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        container = Folder.objects.get(pk=folder_id)

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
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or user_is_contributor
            and is_member
            or user_is_manager
            and is_member
        ):
            add_folder_form = AddFolderForm(request.POST)
            if add_folder_form.is_valid():
                add_folder_form.save()
                return HttpResponseRedirect(
                    reverse("ui-folder-view", args=[container.id])
                )
            root_container = get_root_folder()
            model_list = get_model_list(parent_folder=container, user=request.user)
            return render(
                request,
                "ui/repository.html",
                {
                    "root_container": root_container,
                    "model_list": model_list,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "add_folder_form": add_folder_form,
                    "is_in_project": is_in_project,
                    "project": project,
                    "is_member": is_member,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "show_modal": True,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class FolderDetailsView(View):
    def get(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        folder = Folder.objects.get(pk=folder_id)

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
        ) = checked_project_privileges(request, folder.parent)

        if (
            request.user.is_superuser
            or folder.owner == request.user
            and not user_is_contributor
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):

            model_list = get_model_list(parent_folder=folder, user=request.user)
            return render(
                request,
                "ui/folder-details.html",
                {
                    "root_container": root_container,
                    "folder": folder,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "container": folder,
                    "model_list": model_list,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                    "project": project,
                    "is_member": is_member,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class UpdateFolderView(View):
    def get(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        folder = Folder.objects.get(pk=folder_id)
        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, folder.parent)

        if (
            request.user.username == ADMIN_USERNAME
            or folder.owner == request.user
            and not user_is_contributor
            and not folder.is_system
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):

            update_folder_form = UpdateFolderForm(instance=folder)
            return render(
                request,
                "ui/update-folder.html",
                {
                    "root_container": root_container,
                    "folder": folder,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "container": folder,
                    "update_folder_form": update_folder_form,
                    "user_is_consumer": user_is_consumer,
                    "user_is_editor": user_is_editor,
                    "user_is_contributor": user_is_contributor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                    "project": project,
                    "is_member": is_member,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        folder = Folder.objects.get(pk=folder_id)

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
        ) = checked_project_privileges(request, folder.parent)

        if (
            request.user.is_superuser
            or folder.owner == request.user
            and not user_is_contributor
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):

            update_folder_form = UpdateFolderForm(request.POST, instance=folder)
            if update_folder_form.is_valid():
                update_folder_form.save()
                return HttpResponseRedirect(
                    reverse("ui-folder-details-view", args=[folder.id])
                )
            return render(
                request,
                "ui/update-folder.html",
                {
                    "root_container": root_container,
                    "folder": folder,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "container": folder,
                    "update_folder_form": update_folder_form,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class RecycleFolderView(View):
    def get(self, request, model_id):
        LOGGER = logging.getLogger(__name__)
        folder = Folder.objects.get(pk=model_id)
        container = folder.parent
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
        ) = checked_project_privileges(request, container)

        LOGGER.debug(
            "User permissions for container: {}: user_is_consumer: {}, user_is_contributor: {}, user_is_editor: {}, user_is_manager: {}, project: {}, project_access: {}".format(
                container.get_path(),
                user_is_consumer,
                user_is_contributor,
                user_is_editor,
                user_is_manager,
                project,
                project_access,
            )
        )

        LOGGER.debug(
            "request.user.is_superuser and not folder.is_profile_home_folder? {}; container.owner == request.user and not folder.is_profile_home_folder? {}; user_is_manager and is_member? {}".format(
                request.user.is_superuser and not folder.is_profile_home_folder(),
                container.owner == request.user and not folder.is_profile_home_folder(),
                user_is_manager and is_member,
            )
        )

        if (
            request.user.is_superuser
            and not folder.is_profile_home_folder()
            or container.owner == request.user
            and not folder.is_profile_home_folder()
            and not folder.in_trashcan()
            or user_is_manager
            and is_member
        ):
            profile = Profile.objects.get(user=request.user)
            LOGGER.debug("Recycling folder ...")
            orig_container = recycle_folder(folder, profile)
            return HttpResponseRedirect(
                reverse(
                    "ui-folder-view",
                    args=[
                        orig_container.id,
                    ],
                )
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class DeleteFolderView(View):
    def get(self, request, model_id):
        LOGGER = logging.getLogger(__name__)
        folder = Folder.objects.get(pk=model_id)
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
        ) = checked_project_privileges(request, folder.parent)

        if (
            request.user.is_superuser
            or folder.owner == request.user
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
            or request.user.profile.home_folder != folder
        ):
            orig_container = folder.parent
            LOGGER.debug(
                "Deleting folder (and all children): {} for good.".format(
                    folder.get_path()
                )
            )
            folder.delete()
            return HttpResponseRedirect(
                reverse(
                    "ui-folder-view",
                    args=[
                        orig_container.id,
                    ],
                )
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class RestoreFolderView(View):
    def get(self, request, model_id):
        LOGGER = logging.getLogger(__name__)
        folder = Folder.objects.get(pk=model_id)
        container = folder.orig_parent
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
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or user_is_contributor
            and is_member
            or user_is_manager
            and is_member
        ):
            ts_name = folder.name
            folder.parent = folder.orig_parent
            folder.name = folder.orig_name
            try:
                folder.save()
            except Exception:
                folder.name = ts_name
                folder.save()
            return HttpResponseRedirect(
                reverse(
                    "ui-folder-view",
                    args=[
                        folder.parent.id,
                    ],
                )
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")
