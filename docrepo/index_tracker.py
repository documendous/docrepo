#!/usr/bin/env python

import logging
import os
import sys

import PyPDF2

sys.path.append(".")
os.environ["DJANGO_SETTINGS_MODULE"] = "docrepo.settings"

import django

django.setup()

from docrepo.settings import MEDIA_ROOT
from repo.models.content import ContentFile
from repo.settings import INDEXABLE_TYPES
from transformations.core import generate_pdf_file
from transformations.settings import ALLOWED_PREVIEW_TYPES
from transformations.models import PreviewFile
from repo.models.search import ContentFileIndex


ALLOWED_EXTENSIONS = []

for t in INDEXABLE_TYPES:
    if t not in ALLOWED_EXTENSIONS:
        ALLOWED_EXTENSIONS.append(t)
for t in ALLOWED_PREVIEW_TYPES:
    if t not in ALLOWED_EXTENSIONS:
        ALLOWED_EXTENSIONS.append(t)


class IndexTracker:
    def run_indexer(self, document):
        LOGGER = logging.getLogger(__name__)
        LOGGER.debug("  {}".format(document.parent.get_path()))
        LOGGER.debug("  Using content file: ")
        LOGGER.debug("    {}".format(document.file))
        LOGGER.debug("  Checking first for PreviewFile ...")
        try:
            latest_version = ContentFile.objects.filter(
                parent=document.parent
            ).order_by("-added")[0]
            LOGGER.debug("  Latest version is: {}".format(latest_version))

            preview = PreviewFile.objects.filter(parent=latest_version).order_by(
                "-added"
            )[0]

            pdf_file_obj = open(str("{}/{}").format(MEDIA_ROOT, preview.file), "rb")

            pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
            page_count = pdf_reader.numPages
            LOGGER.debug("    Number of pages: {}".format(page_count))
            i = 0
            text = ""
            while i < page_count:
                pageobj = pdf_reader.getPage(i)
                text += "\n" + pageobj.extractText()
                i += 1
            pdf_file_obj.close()

            index = ContentFileIndex()
            index.content_file = document
            index.text = text.replace("\x00", "", -1)
            try:
                index.save()
                document.is_indexed = True
                document.index_error = None
                document.save()
                LOGGER.info(
                    "Text successfully indexed for {}".format(
                        document.parent.get_path()
                    )
                )

            except Exception as err:
                LOGGER.error("ERR: {}".format(err))
                LOGGER.error("Logging error to contentfile: {}".format(document.id))
                document.is_indexed = True
                document.index_error = repr(err)
                document.save()

        except PreviewFile.DoesNotExist:
            LOGGER.debug("    Unable to find preview file ...")
            LOGGER.debug("    Generating PDF file ...")
            generate_pdf_file(document)

        except IndexError:
            LOGGER.debug("    Unable to find preview file ...")
            LOGGER.debug("    Generating PDF file ...")
            generate_pdf_file(document)

    def run(self):
        LOGGER = logging.getLogger(__name__)
        LOGGER.info("Starting Documendous Index Tracker ...")

        untracked_documents = ContentFile.objects.filter(
            is_indexed=False,
            parent__extension__in=ALLOWED_EXTENSIONS,
        )

        LOGGER.debug("  Indexing the following documents:")
        for document in untracked_documents:
            if document.parent.extension in INDEXABLE_TYPES:
                parent_name = document.parent.name
                _, ext = os.path.splitext(parent_name)
                if ext in INDEXABLE_TYPES:
                    self.run_indexer(document=document)
                else:
                    LOGGER.debug(
                        "  Not allowed to index: {} due to type: {}".format(
                            parent_name, ext
                        )
                    )
        if len(untracked_documents) < 1:
            LOGGER.debug("    No documents to index.")

        LOGGER.debug("  Finished for now.")


if __name__ == "__main__":
    index_tracker = IndexTracker()
    index_tracker.run()
