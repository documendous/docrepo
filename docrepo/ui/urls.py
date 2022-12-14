from django.contrib.auth.decorators import login_required
from django.urls import path


from transformations.views import GeneratePreviewView

from .views.generics import BulkRecycleView, CopyModelsView, MoveModelsView
from .views.projects import (
    ProjectsView,
    AddProjectView,
    RequestMembershipProjectView,
    UpdateProjectView,
    ManageProjectGroupsView,
    JoinOpenProjectView,
    LeaveProjectView,
    ProjectMembershipRequestsView,
)
from .views.index import IndexView

from .views.folders import (
    FolderView,
    FolderDetailsView,
    UpdateFolderView,
    RecycleFolderView,
    DeleteFolderView,
    RestoreFolderView,
)
from search.views import SearchView
from .views.favorites import (
    FavoriteDocumentView,
    FavoriteFolderView,
    FavoritesView,
    UnFavoriteDocumentView,
    UnFavoriteFolderView,
)
from .views.profiles import ProfileDetailsView, UpdateProfileView

from .views.documents import (
    AddDocumentView,
    AddMultiDocsView,
    RecycleDocumentView,
    DocumentView,
    UpdateDocumentView,
    PreviewView,
    DownloadDocumentView,
    UploadNewVersionView,
    DeleteDocumentView,
    RestoreDocumentView,
    DeleteAllView,
)

from ui_custom.urls import urlpatterns as custom_urlpatterns


urlpatterns = [
    path("", login_required(IndexView.as_view()), name="ui-index-view"),
    path(
        "folder/<uuid:folder_id>/",
        login_required(FolderView.as_view()),
        name="ui-folder-view",
    ),
    path("projects/", login_required(ProjectsView.as_view()), name="ui-projects-view"),
    path(
        "search/",
        login_required(SearchView.as_view()),
        name="ui-search-view",
    ),
    path(
        "favorites/<uuid:profile_id>/",
        login_required(FavoritesView.as_view()),
        name="ui-profile-favorites-view",
    ),
    path(
        "document/favorite/<uuid:document_id>/<uuid:profile_id>/<uuid:container_id>/",
        login_required(FavoriteDocumentView.as_view()),
        name="ui-favorite-document-view",
    ),
    path(
        "folder/favorite/<uuid:folder_id>/<uuid:profile_id>/<uuid:container_id>/",
        login_required(FavoriteFolderView.as_view()),
        name="ui-favorite-folder-view",
    ),
    path(
        "document/unfavorite/<uuid:document_id>/<uuid:profile_id>/<uuid:container_id>/",
        login_required(UnFavoriteDocumentView.as_view()),
        name="ui-unfavorite-document-view",
    ),
    path(
        "folder/unfavorite/<uuid:folder_id>/<uuid:profile_id>/<uuid:container_id>/",
        login_required(UnFavoriteFolderView.as_view()),
        name="ui-unfavorite-folder-view",
    ),
    path(
        "profile/details/<uuid:profile_id>/",
        login_required(ProfileDetailsView.as_view()),
        name="ui-profile-details-view",
    ),
    path(
        "profile/<uuid:profile_id>/update/",
        login_required(UpdateProfileView.as_view()),
        name="ui-update-profile-view",
    ),
    path(
        "folder/details/<uuid:folder_id>/",
        login_required(FolderDetailsView.as_view()),
        name="ui-folder-details-view",
    ),
    path(
        "folder/<uuid:folder_id>/document/add/",
        login_required(AddDocumentView.as_view()),
        name="ui-add-document-view",
    ),
    path(
        "folder/<uuid:folder_id>/document/multi-add/",
        login_required(AddMultiDocsView.as_view()),
        name="ui-add-multi-docs-view",
    ),
    path(
        "folder/<uuid:folder_id>/update/",
        login_required(UpdateFolderView.as_view()),
        name="ui-update-folder-view",
    ),
    path(
        "document/<uuid:model_id>/recycle/",
        login_required(RecycleDocumentView.as_view()),
        name="ui-recycle-document-view",
    ),
    path(
        "folder/<uuid:model_id>/recycle/",
        login_required(RecycleFolderView.as_view()),
        name="ui-recycle-folder-view",
    ),
    path(
        "document/details/<uuid:document_id>/",
        login_required(DocumentView.as_view()),
        name="ui-document-view",
    ),
    path(
        "document/<uuid:document_id>/update/",
        login_required(UpdateDocumentView.as_view()),
        name="ui-update-document-view",
    ),
    path(
        "document/genpreview/<uuid:version_id>",
        login_required(GeneratePreviewView.as_view()),
        name="ui-generate-preview",
    ),
    path(
        "document/preview/<uuid:preview_id>",
        login_required(PreviewView.as_view()),
        name="ui-document-preview",
    ),
    path(
        "document/<uuid:document_id>/download/",
        login_required(DownloadDocumentView.as_view()),
        name="ui-download-document-view",
    ),
    path(
        "document/<uuid:document_id>/upload/version/",
        login_required(UploadNewVersionView.as_view()),
        name="ui-upload-new-version-view",
    ),
    path(
        "document/<uuid:model_id>/delete/",
        login_required(DeleteDocumentView.as_view()),
        name="ui-delete-document-view",
    ),
    path(
        "folder/<uuid:model_id>/delete/",
        login_required(DeleteFolderView.as_view()),
        name="ui-delete-folder-view",
    ),
    path(
        "document/<uuid:model_id>/restore/",
        login_required(RestoreDocumentView.as_view()),
        name="ui-restore-document-view",
    ),
    path(
        "folder/<uuid:model_id>/restore/",
        login_required(RestoreFolderView.as_view()),
        name="ui-restore-folder-view",
    ),
    path(
        "recycle/<str:model_ids>/<uuid:profile_id>/",
        login_required(BulkRecycleView.as_view()),
        name="ui-bulk-recycle-view",
    ),
    path(
        "documents/copy/<str:model_ids>/<uuid:folder_id>/",
        login_required(CopyModelsView.as_view()),
        name="ui-folder-select-forcopy-view",
    ),
    path(
        "documents/move/<str:model_ids>/<uuid:folder_id>/",
        login_required(MoveModelsView.as_view()),
        name="ui-folder-select-formove-view",
    ),
    path(
        "project/add/",
        login_required(AddProjectView.as_view()),
        name="ui-add-project-view",
    ),
    path(
        "project/<uuid:project_id>/request/membership/",
        login_required(RequestMembershipProjectView.as_view()),
        name="ui-request-membership-project",
    ),
    path(
        "project/<uuid:project_id>/update/",
        login_required(UpdateProjectView.as_view()),
        name="ui-update-project-view",
    ),
    path(
        "project/<uuid:project_id>/groups/manage/",
        login_required(ManageProjectGroupsView.as_view()),
        name="ui-manage-project-groups-view",
    ),
    path(
        "project/open/join/<uuid:project_id>/",
        login_required(JoinOpenProjectView.as_view()),
        name="ui-join-open-project-view",
    ),
    path(
        "project/<uuid:project_id>/leave/",
        login_required(LeaveProjectView.as_view()),
        name="ui-leave-project-view",
    ),
    path(
        "project/<uuid:project_id>/membership/requests/",
        login_required(ProjectMembershipRequestsView.as_view()),
        name="ui-project-membership-requests-view",
    ),
    path(
        "trashcan/<uuid:folder_id>/delete_all/",
        login_required(DeleteAllView.as_view()),
        name="ui-delete-all-view",
    ),
]


urlpatterns += custom_urlpatterns
