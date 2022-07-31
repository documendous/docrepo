from itertools import chain
import logging
from django.db import models
from repo.model_utils import get_home_folder
from repo.settings import ROOT_FOLDER_NAME
from repo.abstract_models import Base, Ownable, Timestampable, UUIDFieldModel
import repo.models


LOGGER = logging.getLogger(__name__)


class Folder(Base, UUIDFieldModel, Ownable, Timestampable):
    project = None

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="folder_parent",
    )
    orig_parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="folder_orig_parent",
    )

    is_system = models.BooleanField("System Folder", default=False)

    class Meta:
        unique_together = (("name", "parent"),)
        verbose_name = "Folder"
        verbose_name_plural = "Folders"
        ordering = ["name", "parent__name"]

    def children(self):

        model_list = list(
            chain(
                Folder.objects.filter(parent=self),
                repo.models.Document.objects.filter(parent=self),
            )
        )
        return model_list

    def child_folders(self):
        return Folder.objects.filter(parent=self)

    def _build_path(self):
        """Recursive method to build the path based on having a parent"""
        if not self.parent:
            return f"/{self.name}/"
        else:
            return f"{self.parent._build_path()}{self.name}/"

    def _cleaned_path(self, path):
        """Clean path of any unnecessary pieces"""
        return path.rstrip("/")

    def get_path(self):
        """Gets a built path and cleans it up before returning"""
        return self._cleaned_path(self._build_path())

    def path(self):
        return self.get_path()

    def get_nav_path(self):
        def build_path(folder, path_list):
            path_list.append(folder)
            if folder.parent:
                build_path(folder.parent, path_list)
            else:
                return path_list

        def build_nav_path(path_list):
            nav_list = []
            for each in path_list:
                nav_list.append(
                    '<a href="/ui/folder/{}/">{}</a>'.format(each.id, each.name)
                )
            nav_list.reverse()
            nav_link = " / ".join(nav_list)
            return nav_link

        path_list = []
        path_list.append(self)
        if self.parent:
            build_path(self.parent, path_list)
        nav_list = build_nav_path(path_list)
        return nav_list

    def is_project_folder(self):
        """Does not work in templates. See: is_project(). This should be used in views or other Python modules."""
        LOGGER = logging.getLogger(__name__)
        all_projects = repo.models.Project.objects.all()
        for project in all_projects:
            if self.id == project.home_folder.id:
                self.project = project
                LOGGER.debug("Project name is set to: {}".format(self.project.name))
                return {"?": True, "project": project}
        return {"?": False, "project": None}

    def is_project(self):
        """For use in templates."""
        return self.is_project_folder()["?"]

    def is_in_project(self):
        """Returns true if folder is in the path of a project."""
        LOGGER = logging.getLogger(__name__)
        results = self.is_project_folder()
        if results["?"]:
            LOGGER.debug(results)
            return results
        else:
            if self.parent:
                results = self.parent.is_in_project()
                if results["?"]:
                    return results
                else:
                    return results
            else:
                return {"?": False, "project": None}

    def type(self):
        return "folder"

    def is_trashcan(self):
        if self.name == "Trashcan" and self.parent.parent == get_home_folder():
            return True
        return False

    def in_trashcan(self):
        results = self.is_trashcan()
        if results:
            LOGGER.debug(results)
            return results
        else:
            if self.parent:
                results = self.parent.in_trashcan()
                if results:
                    return results
                else:
                    return results
            else:
                return False

    def is_system_folder(self):
        return self.is_system

    def is_profile_home_folder(self):
        home_folders = repo.models.Profile.objects.all().values_list(
            "home_folder", flat=True
        )
        if self.id in home_folders:
            return True
        return False

    def is_open_project(self):
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug("Checking if model is an open project ...")
        result = self.is_in_project()
        is_in_project = result["?"]
        project = result["project"]
        if is_in_project and project:
            LOGGER.debug("Project access? {}".format(project.access))
            if project.access == "open":
                return True
        return False

    def project_members(self):
        in_project = self.is_in_project()
        if in_project["?"]:
            return in_project["project"].members.all()
        else:
            return []

    def __str__(self):
        return self.get_path()
