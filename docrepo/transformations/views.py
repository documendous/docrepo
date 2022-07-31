import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from repo.overflow_models.content import ContentFile
from .core import generate_pdf_file

LOGGER = logging.getLogger(__name__)


class GeneratePreviewView(View):
    def get(self, request, version_id):
        version = ContentFile.objects.get(pk=version_id)
        generate_pdf_file(version)
        return HttpResponseRedirect(
            reverse("ui-document-view", args=[version.parent.id])
        )
