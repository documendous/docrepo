import logging
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from repo.model_utils import get_root_folder
from repo.overflow_models.people import Profile
from repo.settings import (
    APP_NAME,
    FOOTER_TEXT,
)
from ui.forms import UpdateProfileForm

LOGGER = logging.getLogger(__name__)


class ProfileDetailsView(View):
    def get(self, request, profile_id):
        root_container = get_root_folder()
        profile = Profile.objects.get(pk=profile_id)

        if request.user.is_superuser or profile.user == request.user:
            return render(
                request,
                "ui/profile-details.html",
                {
                    "root_container": root_container,
                    "profile": profile,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class UpdateProfileView(View):
    def get(self, request, profile_id):
        profile = Profile.objects.get(pk=profile_id)
        if request.user.is_superuser or profile.user == request.user:
            update_profile_form = UpdateProfileForm(instance=profile)
            root_container = get_root_folder()
            return render(
                request,
                "ui/update-profile.html",
                {
                    "profile": profile,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "update_profile_form": update_profile_form,
                    "root_container": root_container,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, profile_id):
        profile = Profile.objects.get(pk=profile_id)
        if request.user.is_superuser or profile.user == request.user:
            update_profile_form = UpdateProfileForm(request.POST, instance=profile)
            if update_profile_form.is_valid():
                update_profile_form.save()
                return HttpResponseRedirect(
                    reverse("ui-profile-details-view", args=[profile.id])
                )
            root_container = get_root_folder()
            return render(
                request,
                "ui/update-profile.html",
                {
                    "profile": profile,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "update_profile_form": update_profile_form,
                    "root_container": root_container,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")
