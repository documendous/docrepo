import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ui.forms import AddFolderForm
from repo.models.favorites import FavoriteDocument, FavoriteFolder
from repo.models.utils import get_root_folder
from repo.models.people import Profile
from repo.settings import (
    APP_NAME,
    FOOTER_TEXT,
)

from .utils import checked_project_privileges, get_model_list, in_project_path


LOGGER = logging.getLogger(__name__)


class BaseIndexView(View):
    def get(self, request):
        return render(
            request,
            "ui/base/index.html",
            {
                "app_name": APP_NAME,
                "footer_text": FOOTER_TEXT,
                "root_container": get_root_folder(),
            },
        )


class IndexView(View):
    def get(self, request):
        root_container = get_root_folder()
        profile = Profile.objects.get(user=request.user)
        container = profile.home_folder

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

        if container.owner == request.user:

            model_list = get_model_list(parent_folder=container, user=request.user)

            favorite_documents = FavoriteDocument.objects.filter(profile=profile)
            favorite_folders = FavoriteFolder.objects.filter(profile=profile)

            if container.owner == request.user:
                add_folder_form = AddFolderForm(
                    initial={"parent": container, "owner": request.user}
                )
            else:
                add_folder_form = None
            return render(
                request,
                "ui/index.html",
                {
                    "add_folder_form": add_folder_form,
                    "app_name": APP_NAME,
                    "container": container,
                    "footer_text": FOOTER_TEXT,
                    "model_list": model_list,
                    "root_container": root_container,
                    "favorite_documents": favorite_documents,
                    "favorite_folders": favorite_folders,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request):
        LOGGER = logging.getLogger(__name__)
        profile = Profile.objects.get(user=request.user)
        container = profile.home_folder

        if container.owner != request.user:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

        is_in_project, project = in_project_path(parent_folder=container)

        add_folder_form = AddFolderForm(request.POST)

        if add_folder_form.is_valid():
            add_folder_form.save()
            return HttpResponseRedirect(reverse("ui-index-view"))

        LOGGER.debug("Form data is not valid.")

        root_container = get_root_folder()
        model_list = get_model_list(parent_folder=container, user=request.user)

        return render(
            request,
            "ui/folders.html",
            {
                "add_folder_form": add_folder_form,
                "app_name": APP_NAME,
                "container": container,
                "footer_text": FOOTER_TEXT,
                "is_in_project": is_in_project,
                "model_list": model_list,
                "project": project,
                "root_container": root_container,
            },
        )
