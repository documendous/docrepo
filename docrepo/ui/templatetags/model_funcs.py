import logging
from django import template
from repo.overflow_models.favorites import FavoriteDocument, FavoriteFolder
from repo.models import Document, Folder, Profile

LOGGER = logging.getLogger(__name__)

register = template.Library()


@register.filter(name="is_favorited_doc")
def is_favorited_doc(var, args):
    document = Document.objects.get(pk=var)
    profile = Profile.objects.get(pk=args)
    try:
        FavoriteDocument.objects.get(document=document, profile=profile)
        return True
    except FavoriteDocument.DoesNotExist:
        return False


@register.filter(name="is_favorited_folder")
def is_favorited_folder(var, args):
    folder = Folder.objects.get(pk=var)
    profile = Profile.objects.get(pk=args)

    try:
        folder_favorite = FavoriteFolder.objects.get(folder=folder, profile=profile)
        return True
    except FavoriteFolder.DoesNotExist:
        return False


@register.filter(name="past_tense_action")
def past_tense_action(var):
    word = var
    if word == "create":
        return "created"
    if word == "read":
        return "read"
    if word == "update":
        return "updated"
    if word == "delete":
        return "deleted"


@register.filter(name="remove_str")
def remove_str(var, args):
    return var.replace(args, "")
