import uuid
from django.contrib.auth.models import User
from django.db import models


class Base(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    orig_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class BaseDublinCore(Base):
    subject = models.TextField(null=True, blank=True)
    creater = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    contributor = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True)
    dctype = models.CharField(max_length=255, null=True, blank=True)
    format = models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    relation = models.CharField(max_length=255, null=True, blank=True)
    coverage = models.TextField(null=True, blank=True)
    rights = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Ownable(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class UUIDFieldModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Timestampable(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Favorite(UUIDFieldModel, Timestampable):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return "{}".format(self.id)


class UUIDNamedFileField(models.FileField):
    def generate_filename(self, instance, filename):
        # _, ext = os.path.splitext(filename)
        name = f"{uuid.uuid4()}.bin"
        return super().generate_filename(instance, name)
