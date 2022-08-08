from django.contrib.auth.models import User, Group
from django.db import models
from repo.abstract_models import UUIDFieldModel, Base, Ownable, Timestampable


class Project(UUIDFieldModel, Base, Ownable, Timestampable):
    name = models.CharField(max_length=255, unique=True)
    icon = models.ImageField(upload_to="uploads/project_icons/", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    members = models.ManyToManyField(User, related_name="project_members")
    home_folder = models.ForeignKey(
        "Folder", on_delete=models.CASCADE, null=True, blank=True
    )
    access = models.CharField(
        max_length=30,
        choices=(
            ("open", "Open"),
            ("private", "Private"),
            ("public", "Public"),
        ),
        default="public",
    )
    is_active = models.BooleanField(default=True)
    manager_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="project_manager_group",
        null=True,
        blank=True,
    )
    contributor_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="project_contributor_group",
        null=True,
        blank=True,
    )
    editor_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="project_editor_group",
        null=True,
        blank=True,
    )
    consumer_group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="project_consumer_group",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MembershipRequest(UUIDFieldModel, Timestampable):
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="membership_request_from_user"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="membership_request_approver",
    )
    approve_datetime = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (("from_user", "project"),)
        verbose_name = "Membership Request"
        verbose_name_plural = "Membership Requests"

    def __str__(self):
        return "{}/{}/{}".format(self.from_user, self.project.name, self.is_approved)
