SEARCH_METHOD = "postgresql"
INDEXABLE_TYPES = (
    ".doc",
    ".docx",
    ".md",
    ".pdf",
    ".ppt",
    ".pptx",
    ".txt",
    ".xls",
    ".xlsx",
    "",
    ".conf",
    ".xml",
)
MAX_SEARCH_RESULTS = 50

AUTO_DELETE_CONTENT_FILES = False

MAX_EDITED_DOCUMENTS = 25
MAX_VIEWED_DOCUMENTS = 25

### DO NOT CHANGE SETTINGS BELOW

### Application name
APP_NAME = "Documendous"

### Footer text with license info
FOOTER_TEXT = "©2022 Documendous, Inc. All Rights Reserved."

### Version
DEFAULT_DOC_VERSION = "1.0"

### Never change this after initial setup ###
ROOT_FOLDER_NAME = "Root"
HOME_FOLDER_NAME = "Home"
PROJECT_FOLDER_NAME = "Projects"
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@localhost"
ADMIN_PASSWORD = "admin"  # This can be changed in the UI, this is only for init setup.

PROJECT_GROUPS = (
    "manager_group",
    "contributor_group",
    "editor_group",
    "consumer_group",
)
