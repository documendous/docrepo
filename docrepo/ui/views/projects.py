import logging
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from repo.models.utils import get_root_folder
from repo.models.projects import MembershipRequest, Project
from ui.views.utils import checked_project_privileges, set_group_assignments
from ui.forms import AddProjectForm, UpdateProjectForm


LOGGER = logging.getLogger(__name__)


class ProjectsView(View):
    def get(self, request):
        root_container = get_root_folder()

        owned_projects = Project.objects.filter(owner=request.user).order_by(
            "-is_active", "name"
        )
        all_member_projects = Project.objects.filter(
            members__in=[request.user]
        ).order_by("-is_active", "name")

        member_projects = []
        for project in all_member_projects:
            if project not in owned_projects:
                member_projects.append(project)

        if request.user.is_superuser:
            all_projects = Project.objects.filter(is_active=True)
        else:
            all_projects = (
                Project.objects.exclude(access="private")
                .exclude(
                    members__in=[
                        request.user,
                    ]
                )
                .exclude(owner=request.user)
                .exclude(is_active=False)
                .order_by("name")
            )

        return render(
            request,
            "ui/projects.html",
            {
                "owned_projects": owned_projects,
                "all_projects": all_projects,
                "member_projects": member_projects,
                "root_container": root_container,
            },
        )


class AddProjectView(View):
    def get(self, request):
        root_container = get_root_folder()
        add_project_form = AddProjectForm(initial={"members": request.user})
        return render(
            request,
            "ui/add-project.html",
            {"root_container": root_container, "add_project_form": add_project_form},
        )

    def post(self, request):
        add_project_form = AddProjectForm(request.POST)
        if add_project_form.is_valid():
            project = add_project_form.save(commit=False)
            project.owner = request.user
            project.save()
            project.members.add(request.user)
            project.save()
            mgr_group = Group.objects.get(name=project.manager_group)
            request.user.groups.add(mgr_group)
            request.user.save()
            return HttpResponseRedirect(
                reverse(
                    "ui-projects-view",
                )
            )
        root_container = get_root_folder()
        return render(
            request,
            "ui/add-project.html",
            {"root_container": root_container, "add_project_form": add_project_form},
        )


class UpdateProjectView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        root_container = get_root_folder()
        container = project.home_folder

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            _project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or project.owner == request.user
            or user_is_manager
            and is_member
        ):

            update_project_form = UpdateProjectForm(instance=project, request=request)
            return render(
                request,
                "ui/update-project.html",
                {
                    "root_container": root_container,
                    "project": project,
                    "update_project_form": update_project_form,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, project_id):
        LOGGER = logging.getLogger(__name__)
        project = Project.objects.get(pk=project_id)
        container = project.home_folder

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            _project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or project.owner == request.user
            or user_is_manager
            and is_member
        ):
            update_project_form = UpdateProjectForm(
                request.POST, request.FILES, instance=project, request=request
            )
            if update_project_form.is_valid():
                project = update_project_form.save(commit=False)
                if request.user != project.owner and not request.user.is_superuser:
                    project.is_active = True
                project.save()
                update_project_form.save_m2m()
                return HttpResponseRedirect(
                    reverse(
                        "ui-update-project-view",
                        args=[
                            project.id,
                        ],
                    )
                )
            root_container = get_root_folder()
            return render(
                request,
                "ui/update-project.html",
                {
                    "root_container": root_container,
                    "project": project,
                    "update_project_form": update_project_form,
                    "update_project_form": update_project_form,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class JoinOpenProjectView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        LOGGER.debug(
            "User: {} joining open project: {}".format(request.user, project.name)
        )
        if project.access == "open":
            project.members.add(request.user)
            project.save()
            LOGGER.debug(
                "Adding user: {} to project: {} membership".format(
                    request.user, project.name
                )
            )
        else:
            LOGGER.warning("Project: {} is not an open.")
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")
        return HttpResponseRedirect(reverse("ui-projects-view"))


class LeaveProjectView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)
        LOGGER.debug("User: {} leaving project: {}".format(request.user, project.name))
        project.members.remove(request.user)
        return HttpResponseRedirect(reverse("ui-projects-view"))


class RequestMembershipProjectView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        if project.access == "public":
            LOGGER.debug(
                "User: {} requesting membership to project: {}".format(
                    request.user, project.name
                )
            )
            try:
                membership_request = MembershipRequest()
                membership_request.from_user = request.user
                membership_request.project = project
                membership_request.save()
            except IntegrityError as err:
                LOGGER.warn(
                    "User: {} has already requested membership to project: {}".format(
                        request.user, project.name
                    )
                )
            return HttpResponseRedirect(reverse("ui-projects-view"))
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class ProjectMembershipRequestsView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        container = project.home_folder

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            _project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or user_is_manager
            and is_member
        ):
            membership_requests = MembershipRequest.objects.filter(
                project=project, is_approved=False
            )
            root_container = get_root_folder()
            return render(
                request,
                "ui/approve-membership.html",
                {
                    "root_container": root_container,
                    "project": project,
                    "membership_requests": membership_requests,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        container = project.home_folder

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            _project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or _project.owner == request.user
            or user_is_manager
            and is_member
        ):

            approved_ids = request.POST.get("approved_ids").split(",")
            LOGGER.debug("Approved IDs are: {}".format(", ".join(approved_ids)))
            LOGGER.debug(
                "User attempting to approve is: {} on project: {} owned by {}".format(
                    request.user, project.name, project.owner
                )
            )
            for rid in approved_ids:
                membership_request = MembershipRequest.objects.get(pk=rid)
                membership_request.is_approved = True
                membership_request.approve_datetime = timezone.now()
                membership_request.approver = request.user
                membership_request.save()
                project.members.add(membership_request.from_user)
                project.save()
                LOGGER.debug(
                    "Membership request from {} for project {} has been approved by {}".format(
                        membership_request.from_user,
                        project.name,
                        membership_request.approver,
                    )
                )
            return HttpResponseRedirect(
                reverse("ui-project-membership-requests-view", args=[project_id])
            )
        else:
            LOGGER.debug(
                "User attempting to approve is: {} on project: {} owned by {}".format(
                    request.user, project.name, project.owner
                )
            )
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class ManageProjectGroupsView(View):
    def get(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        container = project.home_folder

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            _project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or user_is_manager
            and is_member
        ):

            root_container = get_root_folder()
            return render(
                request,
                "ui/manage-project-groups.html",
                {
                    "root_container": root_container,
                    "project": project,
                },
            )

        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, project_id):
        project = Project.objects.get(pk=project_id)

        container = project.home_folder

        (
            user_is_consumer,
            user_is_editor,
            user_is_contributor,
            user_is_manager,
            is_in_project,
            _project,
            is_member,
            project_access,
        ) = checked_project_privileges(request, container)

        if (
            request.user.is_superuser
            or container.owner == request.user
            or user_is_manager
            and is_member
        ):
            managers = request.POST.getlist("managers")
            contributors = request.POST.getlist("contributors")
            editors = request.POST.getlist("editors")
            consumers = request.POST.getlist("consumers")

            try:

                set_group_assignments(
                    project, managers, contributors, editors, consumers
                )

                return HttpResponseRedirect(
                    reverse("ui-manage-project-groups-view", args=[project_id])
                )

            except Exception as err:
                LOGGER.error(repr(err))
                return render(
                    request,
                    "ui/manage-project-groups.html",
                    {
                        "root_container": get_root_folder(),
                        "project": project,
                    },
                )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")
