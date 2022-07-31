import logging
import os
import sys
import uuid
import django
from django.db import IntegrityError

sys.path.append(".")
os.environ["DJANGO_SETTINGS_MODULE"] = "docrepo.settings"
django.setup()

from docrepo.settings import BASE_DIR
from django.contrib.auth.models import User
from django.core.files import File
from repo.overflow_models.containers import Folder
from repo.overflow_models.content import Document, ContentFile
from repo.model_utils import get_root_folder


class FolderDocsLoader:
    root_folder = get_root_folder()

    def __init__(self):
        self.LOGGER = logging.getLogger(self.__class__.__name__)

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

    def _create_document(self, local_file_name, parent_folder, owner):
        document = Document()
        document.name = os.path.basename(local_file_name)
        self.LOGGER.debug("Document parent is: {}".format(parent_folder))
        document.parent = parent_folder
        document.owner = owner
        document.save()
        return document

    def _create_file(self, _file, parent_folder, owner):
        self.LOGGER.debug(
            "create_file() receives: _file: {}, parent_folder: {}, owner: {}".format(
                _file, parent_folder, owner
            )
        )
        local_file_name = "{}".format(_file)
        self._create_content_file(
            local_file_name,
            document=self._create_document(local_file_name, parent_folder, owner),
        )

    def main(self):
        self.LOGGER.info("Loading Sample Folders and Documents")
        user = User.objects.get(username="testuser1")
        self.LOGGER.info("Using user: {}".format(user))

        try:

            folder1 = Folder.objects.create(
                name="Folder 1", owner=user, parent=user.profile.home_folder
            )
            folder2 = Folder.objects.create(
                name="Folder 2", owner=user, parent=user.profile.home_folder
            )
            folder3 = Folder.objects.create(
                name="Folder 3", owner=user, parent=user.profile.home_folder
            )
            folder11 = Folder.objects.create(
                name="Folder 11", owner=user, parent=folder1
            )
            folder22 = Folder.objects.create(
                name="Folder 22", owner=user, parent=folder2
            )
            folder33 = Folder.objects.create(
                name="Folder 33", owner=user, parent=folder3
            )

            self._create_file(
                _file=BASE_DIR / "demos/sample_folders_docs/data/test1.txt",
                parent_folder=folder1,
                owner=user,
            )
            self._create_file(
                _file=BASE_DIR / "demos/sample_folders_docs/data/test2.txt",
                parent_folder=folder1,
                owner=user,
            )
            self._create_file(
                _file=BASE_DIR / "demos/sample_folders_docs/data/test3.txt",
                parent_folder=folder1,
                owner=user,
            )
            self._create_file(
                _file=BASE_DIR / "demos/sample_folders_docs/data/test1.txt",
                parent_folder=folder22,
                owner=user,
            )
            self._create_file(
                _file=BASE_DIR / "demos/sample_folders_docs/data/test2.txt",
                parent_folder=folder22,
                owner=user,
            )
            self._create_file(
                _file=BASE_DIR / "demos/sample_folders_docs/data/test3.txt",
                parent_folder=folder22,
                owner=user,
            )

        except IntegrityError as err:
            self.LOGGER.info(
                "Seems this has been run already and folders/documents have been populated."
            )

    def run(self):
        self.main()
