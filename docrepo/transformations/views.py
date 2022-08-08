import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

from repo.models.content import ContentFile
from .core import generate_pdf_file


class GeneratePreviewView(View):
    def get(self, request, version_id):
        LOGGER = logging.getLogger(__name__)
        version = ContentFile.objects.get(pk=version_id)
        generate_pdf_file(version)
        return HttpResponseRedirect(
            reverse("ui-document-view", args=[version.parent.id])
        )
