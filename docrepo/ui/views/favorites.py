import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ui.views.utils import checked_project_privileges
from repo.model_utils import get_root_folder
from repo.overflow_models.containers import Folder
from repo.overflow_models.content import Document
from repo.overflow_models.favorites import FavoriteDocument, FavoriteFolder
from repo.overflow_models.people import Profile


LOGGER = logging.getLogger(__name__)


class FavoriteDocumentView(View):
    def get(self, request, document_id, profile_id, container_id):
        document = Document.objects.get(pk=document_id)
        profile = Profile.objects.get(pk=profile_id)
        container = Folder.objects.get(pk=container_id)

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

        if request.user.is_superuser or (
            container.owner == request.user
            and profile == request.user.profile
            and document.owner == request.user
            or is_member
        ):
            favorite = FavoriteDocument()
            favorite.profile = profile
            favorite.document = document
            favorite.save()
            return HttpResponseRedirect(reverse("ui-folder-view", args=[container.id]))
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class FavoriteFolderView(View):
    def get(self, request, folder_id, profile_id, container_id):
        folder = Folder.objects.get(pk=folder_id)
        profile = Profile.objects.get(pk=profile_id)
        container = Folder.objects.get(pk=container_id)

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

        if request.user.is_superuser or (
            container.owner == request.user
            and profile == request.user.profile
            and folder.owner == request.user
            or is_member
        ):
            favorite = FavoriteFolder()
            favorite.profile = profile
            favorite.folder = folder
            favorite.save()
            return HttpResponseRedirect(reverse("ui-folder-view", args=[container.id]))
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class UnFavoriteDocumentView(View):
    def get(self, request, document_id, profile_id, container_id):
        document = Document.objects.get(pk=document_id)
        profile = Profile.objects.get(pk=profile_id)
        container = Folder.objects.get(pk=container_id)

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

        if request.user.is_superuser or (
            container.owner == request.user
            and profile == request.user.profile
            and document.owner == request.user
            or is_member
        ):
            favorite = FavoriteDocument.objects.get(document=document, profile=profile)
            favorite.delete()
            return HttpResponseRedirect(reverse("ui-folder-view", args=[container.id]))
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class UnFavoriteFolderView(View):
    def get(self, request, folder_id, profile_id, container_id):
        folder = Folder.objects.get(pk=folder_id)
        profile = Profile.objects.get(pk=profile_id)
        container = Folder.objects.get(pk=container_id)

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

        if request.user.is_superuser or (
            container.owner == request.user
            and profile == request.user.profile
            and folder.owner == request.user
            or is_member
        ):
            favorite = FavoriteFolder.objects.get(folder=folder, profile=profile)
            favorite.delete()
            return HttpResponseRedirect(reverse("ui-folder-view", args=[container.id]))
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class FavoritesView(View):
    def get(self, request, profile_id):
        profile = Profile.objects.get(pk=profile_id)
        if request.user.is_superuser or profile == request.user.profile:
            favorite_docs = FavoriteDocument.objects.filter(profile=profile)
            favorite_folders = FavoriteFolder.objects.filter(profile=profile)
            root_container = get_root_folder()
            return render(
                request,
                "ui/favorites-list.html",
                {
                    "favorite_docs": favorite_docs,
                    "favorite_folders": favorite_folders,
                    "root_container": root_container,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")
