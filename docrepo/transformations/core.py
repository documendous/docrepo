import logging
import os
import pathlib
import subprocess
import uuid

from django.core.files import File
from docrepo.settings import MEDIA_ROOT
from .models import PreviewFile
from .settings import (
    ALLOWED_PREVIEW_TYPES,
    MAX_PREVIEW_SIZE,
    SOFFICE_EXE,
    SOFFICE_TEMP_DIR,
)


def generate_pdf_file(content_file):
    LOGGER = logging.getLogger(__name__)

    extension = pathlib.Path(content_file.parent.name).suffix

    LOGGER.debug("File to be used for pdf generation: {}".format(content_file.file))
    LOGGER.debug("Document name is: {}".format(content_file.parent.name))
    LOGGER.debug("Logical path: {}".format(content_file.parent.get_path()))
    LOGGER.debug(
        "File extension is: {}".format(pathlib.Path(content_file.parent.name).suffix)
    )
    LOGGER.debug("File size is: {}".format(content_file.file.size))

    if content_file.file.size <= MAX_PREVIEW_SIZE:

        if extension in ALLOWED_PREVIEW_TYPES:
            LOGGER.debug(
                "File: {} has an allowed extension type: {}. Preview transform will be attempted.".format(
                    content_file.file, extension
                )
            )
            LOGGER.debug(
                "Source file is: {}".format(
                    str(MEDIA_ROOT) + os.path.sep + str(content_file.file)
                )
            )
            process = subprocess.Popen(
                [
                    SOFFICE_EXE,
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    SOFFICE_TEMP_DIR,
                    f"{str(MEDIA_ROOT) + os.path.sep + str(content_file.file)}",
                ],
            )
            full_command = " ".join([str(arg) for arg in process.args])
            LOGGER.debug("Using command for transform: {}".format(full_command))
            process.communicate()

            tmp_file = (
                str(SOFFICE_TEMP_DIR)
                + os.path.sep
                + str(content_file.file).split("/")[-1].split(".")[0]
                + ".pdf"
            )
            LOGGER.debug("Temp file for upload is {}".format(tmp_file))
            generate_preview_file(content_file, tmp_file)
        elif extension == ".pdf":
            generate_preview_file(
                content_file,
                str(
                    "{}/{}".format(
                        MEDIA_ROOT,
                        content_file.file,
                    )
                ),
                src_is_content_file=True,
            )
        else:
            LOGGER.warning(
                "File: {} does not have an allowed extension type which is: {}. Preview transform will not be attempted. Allowed transformations only for extensions: {}".format(
                    content_file.file, extension, (", ").join(ALLOWED_PREVIEW_TYPES)
                )
            )

    else:
        LOGGER.warning(
            "File: {} size is {}. Max size allowed for preview transformation is: {} Preview transform will not be attempted.".format(
                content_file.file, content_file.file.size, MAX_PREVIEW_SIZE
            )
        )


def get_pdf_file(instance):
    return generate_pdf_file(instance)


def generate_preview_file(version, tmp_file, src_is_content_file=False):
    LOGGER = logging.getLogger(__name__)
    content_file = version
    try:
        LOGGER.debug("Generating preview file from {}".format(str(tmp_file)))
        local_file = open(str(tmp_file), "rb")
        djangofile = File(local_file)
        preview_file = PreviewFile()
        preview_file.parent = content_file
        preview_file.file.save(str(uuid.uuid4()) + ".bin", djangofile)
        preview_file.save()
        local_file.close()
        LOGGER.debug(
            "Preview file creation successful. Removing temp file: {}".format(tmp_file)
        )
        if not src_is_content_file:
            os.remove(str(tmp_file))
        return True
    except FileNotFoundError as err:
        LOGGER.error(repr(err))
        LOGGER.error("Logging error to contentfile: {}".format(content_file.id))
        content_file.is_indexed = True
        content_file.index_error = "Error: {}".format(repr(err))
        content_file.save()
        return False
