# Transformations
from docrepo.settings import BASE_DIR

SOFFICE_EXE = "/usr/bin/soffice"
SOFFICE_TEMP_DIR = BASE_DIR / "contentfiles/tmp"
ALLOWED_PREVIEW_TYPES = (
    ".doc",
    ".docx",
    ".gif",
    ".jpg",
    ".jpeg",
    ".md",
    ".png",
    ".ppt",
    ".pptx",
    ".txt",
    ".xls",
    ".xlsx",
    "",
    ".conf",
    ".xml",
)
MAX_PREVIEW_SIZE = 10000000  # bytes
