from django.shortcuts import render
from django.views import View

from repo.model_utils import get_root_folder
from repo.settings import SEARCH_METHOD
from ui.views.search_utils import postgresql_search


class SearchView(View):
    def get(self, request):
        root_container = get_root_folder()
        search_term = self.request.GET.get("search_term")
        if search_term and SEARCH_METHOD == "postgresql":
            results = postgresql_search(search_term, request)
        else:
            results = None

        return render(
            request,
            "ui/search.html",
            {
                "root_container": root_container,
                "search_term": search_term,
                "search_results": results,
            },
        )
