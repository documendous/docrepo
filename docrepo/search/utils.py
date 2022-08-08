import logging

from django.contrib.postgres.search import SearchQuery, SearchVector

from ui.views.utils import checked_project_privileges
from repo.models.containers import Folder
from repo.models.content import Document
from repo.models.search import ContentFileIndex
from repo.settings import MAX_SEARCH_RESULTS


def get_content_hits(search_query):
    LOGGER = logging.getLogger(__name__)
    LOGGER.debug("  Querying full text.")
    return ContentFileIndex.objects.annotate(
        search=SearchVector(
            "text",
        ),
    ).filter(search=search_query)


def get_document_metadata_hits(search_query):
    LOGGER = logging.getLogger(__name__)
    LOGGER.debug("  Querying against document metadata.")
    return Document.objects.annotate(
        search=SearchVector(
            "name",
            "title",
            "description",
        ),
    ).filter(search=search_query)


def get_folder_metadata_hits(search_query):
    LOGGER = logging.getLogger(__name__)
    LOGGER.debug("  Querying against folder metadata.")
    return Folder.objects.annotate(
        search=SearchVector(
            "name",
            "title",
            "description",
        ),
    ).filter(search=search_query)


def get_search_results(
    content_index_exact_hits, document_exact_hits, folder_exact_hits, request
):
    LOGGER = logging.getLogger(__name__)
    results = []

    for hit in content_index_exact_hits:
        if hit.content_file.parent not in results:
            if len(results) < MAX_SEARCH_RESULTS:
                results.append(
                    {
                        "document": hit.content_file.parent,
                        "search_type": "full_text",
                        "type": "document",
                        "version": hit.content_file.parent.latest_version().version,
                    }
                )

    for hit in document_exact_hits:
        if hit not in results:
            if len(results) < MAX_SEARCH_RESULTS:
                results.append(
                    {"document": hit, "search_type": "metadata", "type": "document"}
                )

    for hit in folder_exact_hits:
        if hit not in results:
            if len(results) < MAX_SEARCH_RESULTS:
                results.append(
                    {"document": hit, "search_type": "metadata", "type": "folder"}
                )

    secure_results = []
    for row in results:
        if "document" in row:
            container = row["document"].parent
            document = row["document"]

            LOGGER.debug(
                "Checking user's project permissions for document: {}".format(document)
            )
            (
                user_is_consumer,
                user_is_editor,
                user_is_contributor,
                user_is_manager,
                is_in_project,
                project,
                is_member,
                project_access,
            ) = checked_project_privileges(request, container)

            if (
                request.user.is_superuser
                or document.owner == request.user
                or user_is_consumer
                and is_member
                or user_is_editor
                and is_member
                or user_is_contributor
                and is_member
                or user_is_manager
                and is_member
                or project_access == "open"
            ):
                secure_results.append(row)
    return secure_results


def postgresql_search(search_term, request):
    LOGGER = logging.getLogger(__name__)
    LOGGER.debug("Search Term is: {}".format(search_term))

    LOGGER.debug("Performing search query.")
    LOGGER.debug("  Querying against full text content.")

    search_query = SearchQuery(search_term)
    LOGGER.debug("  Using Search Query: {}".format(search_query))

    content_index_exact_hits = get_content_hits(search_query=search_query)
    document_exact_hits = get_document_metadata_hits(search_query=search_query)
    folder_exact_hits = get_folder_metadata_hits(search_query=search_query)
    results = get_search_results(
        content_index_exact_hits=content_index_exact_hits,
        document_exact_hits=document_exact_hits,
        folder_exact_hits=folder_exact_hits,
        request=request,
    )

    LOGGER.debug("  Results: {}".format(results))
    return results
