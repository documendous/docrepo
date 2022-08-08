from django.forms import ModelForm
from django import forms
from repo.models.containers import Folder
from repo.models.content import Document, ContentFile
from repo.models.people import Profile
from repo.models.projects import Project


class AddFolderForm(ModelForm):
    class Meta:
        model = Folder
        fields = ["name", "title", "description", "parent", "owner"]
        widgets = {
            "parent": forms.HiddenInput(),
            "owner": forms.HiddenInput(),
        }


class UpdateFolderForm(ModelForm):
    class Meta:
        model = Folder
        fields = [
            "name",
            "title",
            "description",
        ]


class AddDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = [
            "name",
            "title",
            "description",
            "parent",
            "owner",
            "subject",
            "creater",
            "publisher",
            "contributor",
            "created",
            "format",
            "identifier",
            "source",
            "language",
            "relation",
            "coverage",
            "rights",
        ]
        widgets = {
            "parent": forms.HiddenInput(),
            "owner": forms.HiddenInput(),
        }


class UpdateDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = [
            "name",
            "title",
            "description",
            "parent",
            "owner",
            "subject",
            "creater",
            "publisher",
            "contributor",
            "created",
            "format",
            "identifier",
            "source",
            "language",
            "relation",
            "coverage",
            "rights",
        ]


class AddContentfileForm(ModelForm):
    class Meta:
        model = ContentFile
        fields = ["file"]


class AddMultiContentfileForm(ModelForm):
    file = forms.FileField(widget=forms.ClearableFileInput(attrs={"multiple": True}))

    class Meta:
        model = ContentFile
        fields = ["file"]


class AddProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "title",
            "description",
            "access",
        ]


class UpdateProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "title",
            "icon",
            "description",
            "members",
            "access",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        project = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        if project.owner != self.request.user:
            del self.fields["is_active"]


class UpdateProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            "bio",
            "location",
            "position",
            "slack",
            "skype",
            "linkedin_profile_url",
        ]


class UploadNewVersionForm(ModelForm):
    class Meta:
        model = ContentFile
        fields = [
            "file",
            "version_type",
        ]
