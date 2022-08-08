import logging
import os

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from docrepo.settings import BASE_DIR, MEDIA_ROOT
from transformations.models import PreviewFile
from transformations.settings import ALLOWED_PREVIEW_TYPES, MAX_PREVIEW_SIZE
from repo.models.people import Profile
from repo.models.content import ContentFile, Document
from repo.models.utils import get_root_folder
from repo.models.containers import Folder
from repo.constants import ADMIN_USERNAME
from repo.settings import APP_NAME, FOOTER_TEXT
from ui.forms import (
    AddContentfileForm,
    AddMultiContentfileForm,
    AddDocumentForm,
    UpdateDocumentForm,
    UploadNewVersionForm,
)
from ui.views.utils import (
    checked_project_privileges,
    create_content_file,
    get_new_version,
    recycle_document,
)


class AddDocumentView(View):
    def get(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        container = Folder.objects.get(pk=folder_id)
        add_document_form = AddDocumentForm(
            initial={"owner": request.user, "parent": container}
        )
        add_contentfile_form = AddContentfileForm()

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

            return render(
                request,
                "ui/add-document-view.html",
                {
                    "root_container": root_container,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "add_document_form": add_document_form,
                    "add_contentfile_form": add_contentfile_form,
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

            add_document_form = AddDocumentForm(request.POST)
            add_contentfile_form = AddContentfileForm(request.POST, request.FILES)

            if add_document_form.is_valid() and add_contentfile_form.is_valid():
                document = add_document_form.save()
                contentfile = add_contentfile_form.save(commit=False)
                contentfile.parent = document
                contentfile.save()
                document.content_files.add(contentfile)
                document.save()
                return HttpResponseRedirect(
                    reverse("ui-folder-view", args=[container.id])
                )
            root_container = get_root_folder()
            return render(
                request,
                "ui/add-document-view.html",
                {
                    "root_container": root_container,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "add_document_form": add_document_form,
                    "add_contentfile_form": add_contentfile_form,
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


class AddMultiDocsView(View):
    def get(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
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

            add_contentfile_form = AddMultiContentfileForm()
            return render(
                request,
                "ui/add-multi-documents-view.html",
                {
                    "root_container": root_container,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "add_contentfile_form": add_contentfile_form,
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

    def post(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
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

            form = AddContentfileForm(request.POST, request.FILES)
            files = request.FILES.getlist("file")
            if form.is_valid():
                for f in files:
                    doc_name = os.path.basename(str(f))
                    document = Document()
                    document.name = doc_name
                    document.owner = request.user
                    document.parent = container
                    try:
                        document.save()
                        create_content_file(f, document)
                        messages.success(
                            self.request,
                            "Successfully added file: {}".format(document.name),
                        )
                    except IntegrityError as err:
                        error_msg = "Cannot create file because it already exists here."
                        LOGGER.warn(error_msg)
                        messages.warning(
                            self.request,
                            "Unable to add file: {}. It already exists in this space.".format(
                                doc_name
                            ),
                        )

                return HttpResponseRedirect(
                    reverse(
                        "ui-add-multi-docs-view",
                        args=[
                            container.id,
                        ],
                    )
                )
            return render(
                request,
                "ui/add-multi-documents-view.html",
                {
                    "root_container": root_container,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "add_contentfile_form": form,
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


class RecycleDocumentView(View):
    def get(self, request, model_id):
        LOGGER = logging.getLogger(__name__)
        profile = Profile.objects.get(user=request.user)
        document = Document.objects.get(pk=model_id)
        container = document.parent

        LOGGER.debug("Container is {}".format(container))

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
            "request.user.is_superuser? {}; container.owner == request.user? {}; user_is_manager and is_member? {}".format(
                request.user.is_superuser,
                container.owner == request.user,
                user_is_manager and is_member,
            )
        )

        if (
            request.user.is_superuser
            or container.owner == request.user
            or user_is_manager
            and is_member
        ):
            orig_container = recycle_document(document, profile)
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


class DocumentView(View):
    def get(self, request, document_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        document = Document.objects.get(pk=document_id)

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
        ) = checked_project_privileges(request, document.parent)

        if (
            request.user.is_superuser
            or document.owner == request.user
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

            latest_version = ContentFile.objects.filter(parent=document).order_by(
                "-added"
            )[0]

            try:
                preview = PreviewFile.objects.filter(parent=latest_version).order_by(
                    "-added"
                )[0]
            except IndexError:
                preview = None
            except PreviewFile.DoesNotExist:
                preview = None
            container = document.parent
            return render(
                request,
                "ui/document-view.html",
                {
                    "root_container": root_container,
                    "document": document,
                    "preview": preview,
                    "container": container,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "latest_version": latest_version,
                    "allowed_preview_types": ALLOWED_PREVIEW_TYPES,
                    "max_preview_size": MAX_PREVIEW_SIZE,
                    "user_is_consumer": user_is_consumer,
                    "user_is_contributor": user_is_contributor,
                    "user_is_editor": user_is_editor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                    "project": project,
                    "is_member": is_member,
                    "ADMIN_USERNAME": ADMIN_USERNAME,
                    "project_access": project_access,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class UpdateDocumentView(View):
    def get(self, request, document_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        document = Document.objects.get(pk=document_id)

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
        ) = checked_project_privileges(request, document.parent)

        if (
            request.user.username == ADMIN_USERNAME
            or document.owner == request.user
            and not user_is_contributor
            and not user_is_consumer
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):

            update_document_form = UpdateDocumentForm(instance=document)
            return render(
                request,
                "ui/update-document.html",
                {
                    "root_container": root_container,
                    "document": document,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "container": document.parent,
                    "update_document_form": update_document_form,
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

    def post(self, request, document_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        document = Document.objects.get(pk=document_id)

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
        ) = checked_project_privileges(request, document.parent)

        if (
            request.user.username == ADMIN_USERNAME
            or document.owner == request.user
            and not user_is_contributor
            and not user_is_consumer
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):

            update_document_form = UpdateDocumentForm(request.POST, instance=document)
            if update_document_form.is_valid():
                update_document_form.save()
                return HttpResponseRedirect(
                    reverse("ui-document-view", args=[document.id])
                )
            return render(
                request,
                "ui/update-document.html",
                {
                    "root_container": root_container,
                    "document": document,
                    "app_name": APP_NAME,
                    "footer_text": FOOTER_TEXT,
                    "container": document.parent,
                    "update_document_form": update_document_form,
                    "user_is_consumer": user_is_consumer,
                    "user_is_editor": user_is_editor,
                    "user_is_contributor": user_is_contributor,
                    "user_is_manager": user_is_manager,
                    "is_in_project": is_in_project,
                    "project": project,
                    "is_member": is_member,
                    "project_access": project_access,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class PreviewView(View):
    def get(self, request, preview_id):
        LOGGER = logging.getLogger(__name__)
        preview = PreviewFile.objects.get(pk=preview_id)
        preview_file = str(MEDIA_ROOT) + os.path.sep + str(preview.file)
        LOGGER.debug("preview_file: {}".format(preview_file))
        container = preview.parent.parent.parent

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
            request.user.username == ADMIN_USERNAME
            or container.owner == request.user
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

            with open(preview_file, "rb") as pdf:
                response = HttpResponse(pdf.read(), content_type="application/pdf")
                response["Content-Disposition"] = f"inline;filename={preview_file}"
                return response
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class DownloadDocumentView(View):
    def get(self, request, document_id):
        LOGGER = logging.getLogger(__name__)
        document = Document.objects.get(pk=document_id)
        content_file = document.latest_version()
        container = content_file.parent.parent

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
            request.user.username == ADMIN_USERNAME
            or container.owner == request.user
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
            filepath = str(BASE_DIR / "contentfiles" / str(content_file.file))
            LOGGER.debug("Download request for: {}".format(filepath))
            if os.path.exists(filepath):
                with open(filepath, "rb") as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/force-download"
                    )
                    response["Content-Disposition"] = (
                        "inline; filename=" + document.name
                    )
                    return response

            LOGGER.warning("filepath: {} does not exist.".format(filepath))
            raise Http404
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class UploadNewVersionView(View):
    def get(self, request, document_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        document = Document.objects.get(pk=document_id)
        container = document.parent

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
            request.user.username == ADMIN_USERNAME
            or document.owner == request.user
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):

            upload_new_version_form = UploadNewVersionForm()
            return render(
                request,
                "ui/upload-new-version.html",
                {
                    "root_container": root_container,
                    "document": document,
                    "upload_new_version_form": upload_new_version_form,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")

    def post(self, request, document_id):
        LOGGER = logging.getLogger(__name__)
        root_container = get_root_folder()
        document = Document.objects.get(pk=document_id)
        upload_new_version_form = UploadNewVersionForm(request.POST, request.FILES)

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
        ) = checked_project_privileges(request, document.parent)

        if (
            request.user.username == ADMIN_USERNAME
            or document.owner == request.user
            or user_is_editor
            and is_member
            or user_is_manager
            and is_member
        ):
            if upload_new_version_form.is_valid():
                content_file = upload_new_version_form.save(commit=False)
                content_file.parent = document
                content_file.version = get_new_version(
                    content_file, content_file.version_type
                )
                content_file.save()

                return HttpResponseRedirect(
                    reverse("ui-document-view", args=[document.id])
                )
            return render(
                request,
                "ui/upload-new-version.html",
                {
                    "root_container": root_container,
                    "document": document,
                    "upload_new_version_form": upload_new_version_form,
                },
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class DeleteDocumentView(View):
    def get(self, request, model_id):
        LOGGER = logging.getLogger(__name__)
        document = Document.objects.get(pk=model_id)
        orig_container = document.parent
        container = orig_container

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
            or user_is_manager
            and is_member
        ):
            LOGGER.debug("Deleting document: {} for good.".format(document.get_path()))
            document.delete()
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


class RestoreDocumentView(View):
    def get(self, request, model_id):
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug("USER IS LOGGED IN? {}".format(request.user.is_authenticated))
        document = Document.objects.get(pk=model_id)
        ts_name = document.name
        LOGGER.debug("Document's original parent is: {}".format(document.orig_parent))
        document.parent = document.orig_parent
        document.name = document.orig_name
        LOGGER.debug("Document's parent is: {}".format(document.parent))
        container = document.parent

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
            try:
                document.save()
            except Exception:
                document.name = ts_name
                document.save()
            return HttpResponseRedirect(
                reverse(
                    "ui-folder-view",
                    args=[document.parent.id],
                )
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")


class DeleteAllView(View):
    def get(self, request, folder_id):
        LOGGER = logging.getLogger(__name__)
        container = Folder.objects.get(pk=folder_id)

        if request.user.is_superuser or container.owner == request.user:
            LOGGER.debug(
                "Emptying trashcan for user: {}; Permanently deleting all objects.".format(
                    request.user
                )
            )
            folders = Folder.objects.filter(parent=container)
            documents = Document.objects.filter(parent=container)

            for folder in folders:
                folder.delete()
                LOGGER.debug("  Permanently deleting folder: {}".format(folder.name))

            for document in documents:
                document.delete()
                LOGGER.debug(
                    "  Permanently deleting document: {}".format(document.name)
                )

            return HttpResponseRedirect(
                reverse(
                    "ui-folder-view",
                    args=[
                        container.id,
                    ],
                )
            )
        else:
            LOGGER.warning("Unauthorized action by: {}".format(request.user))
            raise PermissionDenied("Unauthorized action.")
