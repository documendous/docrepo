from django.contrib.auth.models import User
from demos.loaders import DemoLoader
from .users import user_list

admin_user = User.objects.get(username="admin")

from .settings import (
    org_name,
    user_password,
    org_description,
    admin_user,
    org_website,
    project_name,
    project_title,
    project_description,
    project_admin,
    project_access,
    project_doc_path,
    demo_name,
)


class PhoenixProjectLoader(DemoLoader):

    user_list = user_list
    org_name = org_name
    user_password = user_password
    org_description = org_description
    admin_user = admin_user
    org_website = org_website
    project_name = project_name
    project_title = project_title
    project_description = project_description
    project_admin = project_admin
    project_access = project_access
    project_doc_path = project_doc_path
    demo_name = demo_name


loader = PhoenixProjectLoader()
loader.run()
