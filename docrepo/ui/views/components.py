from django.shortcuts import render
from django.views import View
from docrepo.settings import CURRENT_VERSION

from repo.settings import FOOTER_TEXT


class FooterComponent(View):
    def get(self, request):
        return render(
            request,
            "ui/base/footer.html",
            {"footer_text": FOOTER_TEXT, "current_version": CURRENT_VERSION},
        )
