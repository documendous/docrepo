import logging
import os
import uuid

from django.contrib.auth.models import User, Group
from django.core.files import File

from docrepo.settings import BASE_DIR
from repo.models.projects import Project
from repo.models.people import Profile, Organization
from repo.models.content import Document, ContentFile
from repo.models.containers import Folder


class DemoLoader:

    user_list = []
    org_name = ""
    user_password = ""
    org_description = ""
    admin_user = ""
    org_website = ""
    project_name = ""
    project_title = ""
    project_description = ""
    project_admin = ""
    project_access = ""
    project_doc_path = ""

    def __init__(self):
        self.LOGGER = logging.getLogger(self.__class__.__name__)

    def _create_demo(self):
        org = self._create_organization()
        self._create_all_users(org)
        self._assign_all_users(self._create_project())

    def run(self):

        self.LOGGER.info("Running {} ...".format(self.demo_name))
        self.LOGGER.info("Creating organization: {}".format(self.org_name))
        self._create_demo()
        self.LOGGER.info("  Done.")

    def _create_all_users(self, org):
        for user in self.user_list:
            self.LOGGER.info("Creating User: {} Org: {}".format(user, org))
            self._create_user(user=user, organization=org)

    def _assign_all_users(self, project):
        for user in self.user_list:
            self.LOGGER.info("Assigning to groups")
            self._assign_groups(user=user)

    def _add_to_group(self, username, group):
        u = User.objects.get(username=username)
        u.groups.add(group)
        u.save()

    def _assign_groups(self, user):
        self.LOGGER.info(
            "Assigning user: {} to group: {}".format(user["username"], user["group"])
        )
        self._add_to_group(
            username=user["username"], group=Group.objects.get(name=user["group"])
        )

    def _create_user(self, user, organization):
        try:
            User.objects.get(username=user["username"])
            self.LOGGER.info("User [{}] already created.".format(user["username"]))
        except User.DoesNotExist:
            self.LOGGER.info("Creating user [{}].".format(user["username"]))
            self._add_user(user=user, organization=organization)

    def _add_user(self, user, organization):
        u = User()
        for k, v in user.items():
            setattr(u, k, v)
        u.set_password(self.user_password)
        u.save()
        self._set_profile(user_obj=u, user_data=user, organization=organization)

    def _set_profile(self, user_obj, user_data, organization):
        self.LOGGER.debug("Setting profile for user: {}".format(user_obj))
        self.LOGGER.debug(
            "Using data: position: {} organization: {}".format(
                user_data["position"], organization
            )
        )
        profile = Profile.objects.get(user=user_obj)
        profile.position = user_data["position"]
        profile.organization = organization
        profile.save()

    def _create_document(self, local_file_name, parent_folder, owner):
        document = Document()
        document.name = os.path.basename(local_file_name)
        self.LOGGER.debug("Document parent is: {}".format(parent_folder))
        document.parent = parent_folder
        document.owner = owner
        document.save()
        return document

    def _create_content_file(self, local_file_name, document):
        local_file = open(local_file_name, "rb")
        djangofile = File(local_file)
        content_file = ContentFile()
        self.LOGGER.debug("ContentFile will be: {}".format(djangofile))
        content_file.parent = document
        content_file.file.save(str(uuid.uuid4()) + ".bin", djangofile)
        content_file.save()
        local_file.close()
        document.content_files.add(content_file)
        document.save()

    def _create_file(self, _file, root_folder, parent_folder, owner):
        self.LOGGER.debug(
            "create_file() receives: _file: {}, root_folder: {}, parent_folder: {}, owner: {}".format(
                _file, root_folder, parent_folder, owner
            )
        )
        local_file_name = "{}/{}".format(root_folder, _file)
        self._create_content_file(
            local_file_name,
            document=self._create_document(local_file_name, parent_folder, owner),
        )

    def _create_folder(self, folder_name, owner, logical_folder):
        folder = Folder()
        folder.name = folder_name[0].title()
        folder.owner = owner
        folder.parent = logical_folder
        folder.save()
        return folder

    def _ingest(self, local_data_dir, logical_folder, owner):
        self.LOGGER.debug("Starting ingesting ...")
        self.LOGGER.info(
            "Ingesting from {} into {}".format(
                local_data_dir, logical_folder.get_path()
            )
        )

        for (root, _, files) in os.walk(local_data_dir, topdown=True):
            folder_name = root.split("/")[-1:]
            self.LOGGER.debug(
                "Creating folder: {} in {}".format(
                    folder_name[0].title(), logical_folder.get_path()
                )
            )
            folder = self._create_folder(
                folder_name=folder_name, owner=owner, logical_folder=logical_folder
            )
            for f in files:
                self.LOGGER.debug(
                    "Creating file: {}, root: {}, parent: {}, owner: {}".format(
                        f, root, folder, owner
                    )
                )
                self._create_file(
                    _file=f, root_folder=root, parent_folder=folder, owner=owner
                )
        self.LOGGER.debug("Ingesting finished.")

    def _add_organization(self):
        org = Organization()
        org.name = self.org_name
        org.description = self.org_description
        org.owner = self.admin_user
        org.website = self.org_website
        org.save()
        return org

    def _create_organization(self):
        try:
            org = Organization.objects.get(name=self.org_name)
            self.LOGGER.info("Organization [{}] already created.".format(self.org_name))
        except Organization.DoesNotExist:
            org = self._add_organization()
        self.LOGGER.debug("Returning organization: {}".format(org))
        return org

    def _add_project(self):
        project = Project()
        project.name = self.project_name
        project.title = self.project_title
        project.description = self.project_description
        project.owner = User.objects.get(username=self.project_admin)
        project.access = self.project_access
        project.save()
        return project

    def _add_project_folder(self, project):
        folder = Folder()
        folder.name = "Documents"
        folder.title = "Phoenix Project Documents"
        folder.owner = User.objects.get(username=self.project_admin)
        self.LOGGER.debug("Project Home Folder is: {}".format(project.home_folder))
        folder.parent = project.home_folder
        folder.save()
        return folder

    def _add_project_members(self, project):
        for user in self.user_list:
            project.members.add(User.objects.get(username=user["username"]))
        project.save()

    def _create_project(self):
        try:
            project = Project.objects.get(name=self.project_name)
            self.LOGGER.debug("Found project: {}".format(project))
            self.LOGGER.info("Project {} already created.".format(self.project_name))
        except Project.DoesNotExist:
            self.LOGGER.info("Creating project [{}].".format(self.project_name))
            project = self._add_project()
            folder = self._add_project_folder(project=project)
            self._add_project_members(project=project)
            self._ingest(
                BASE_DIR / self.project_doc_path,
                folder,
                User.objects.get(username=self.project_admin),
            )
        return project
