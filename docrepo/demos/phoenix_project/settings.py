from django.contrib.auth.models import User

demo_name = "Phoenix Project Demo"
admin_user = User.objects.get(username="admin")
project_name = "Phoenix"
project_title = "Phoenix Project"
project_description = "An example project based on the book: The Phoenix Project"
project_admin = "billpalmer"
project_access = "public"
user_password = "S3cr3t"
project_doc_path = "demos/phoenix_project/data/documents"
org_name = "Parts Unlimited"
org_description = "Auto parts company in Anywhere, USA"
org_website = "https://partsunlimit.com"
