from django.contrib.auth.models import User
from django.db import models
from repo.abstract_models import UUIDFieldModel, Base, Ownable, Timestampable


class Organization(UUIDFieldModel, Base, Ownable, Timestampable):
    name = models.CharField(max_length=255, unique=True)
    website = models.URLField(null=True, blank=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        ordering = [
            "name",
        ]

    def __str__(self):
        return self.name


class Profile(UUIDFieldModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=30, null=True, blank=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    slack = models.CharField(max_length=50, null=True, blank=True)
    skype = models.CharField(max_length=50, null=True, blank=True)
    linkedin_profile_url = models.URLField("LinkedIn URL", null=True, blank=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    home_folder = models.ForeignKey(
        "Folder",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="profile_home_folder",
    )
    trashcan_folder = models.ForeignKey(
        "Folder",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="profile_trashcan_folder",
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        ordering = ["user__username"]

    def __str__(self):
        return self.user.username
