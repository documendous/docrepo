from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from repo.models.content import (
    Document,
    ContentFile,
)
from repo.models.containers import Folder
from repo.models.people import Organization, Profile
from repo.models.projects import Project
from repo.models.favorites import FavoriteDocument, FavoriteFolder


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "is_staff"]


class ContentFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContentFile
        fields = ["id", "file", "version", "parent"]


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "name",
            "title",
            "description",
            "owner",
            "added",
            "modified",
            "subject",
            "creater",
            "publisher",
            "contributor",
            "created",
            "type",
            "format",
            "identifier",
            "source",
            "language",
            "relation",
            "coverage",
            "rights",
            "content_files",
            "parent",
            "path",
        ]


class FolderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Folder
        fields = [
            "id",
            "name",
            "title",
            "description",
            "owner",
            "added",
            "modified",
            "parent",
            "path",
        ]


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "website"]


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "bio",
            "location",
            "position",
            "slack",
            "skype",
            "linkedin_profile_url",
            "organization",
            "home_folder",
            "trashcan_folder",
        ]


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "icon",
            "title",
            "description",
            "owner",
            "added",
            "modified",
        ]


class FavoriteFolderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FavoriteFolder
        fields = [
            "id",
            "profile",
            "folder",
        ]


class FavoriteDocumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FavoriteDocument
        fields = [
            "id",
            "profile",
            "document",
        ]


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ContentFileViewSet(viewsets.ModelViewSet):
    queryset = ContentFile.objects.all()
    serializer_class = ContentFileSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class FavoriteFolderViewSet(viewsets.ModelViewSet):
    queryset = FavoriteFolder.objects.all()
    serializer_class = FavoriteFolderSerializer


class FavoriteDocumentViewSet(viewsets.ModelViewSet):
    queryset = FavoriteDocument.objects.all()
    serializer_class = FavoriteDocumentSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"contentfiles", ContentFileViewSet)
router.register(r"documents", DocumentViewSet)
router.register(r"folders", FolderViewSet)
router.register(r"organizations", OrganizationViewSet)
router.register(r"profiles", ProfileViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"favorite_folders", FavoriteFolderViewSet)
router.register(r"favorite_documents", FavoriteDocumentViewSet)
