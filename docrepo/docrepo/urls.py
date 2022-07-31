from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from docrepo.settings import MEDIA_ROOT, MEDIA_URL
from ui.views.index import BaseIndexView
from ui.views.components import FooterComponent
from repo.serializers import router


urlpatterns = [
    path("grappelli/", include("grappelli.urls")),
    path("admin/", admin.site.urls),
    path(
        "ui/auth/",
        include("django.contrib.auth.urls"),
    ),
    path("ui/", include("ui.urls")),
    path("", BaseIndexView.as_view(), name="base-index-view"),
    path("footer-view", FooterComponent.as_view(), name="base-footer-view"),
    path("services/api/", include(router.urls)),
    path("services/api-auth/", include("rest_framework.urls")),
]

urlpatterns += static(MEDIA_URL, document_root=str(MEDIA_ROOT) + "/uploads")
