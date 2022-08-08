from django import template
from repo.models.favorites import FavoriteDocument, FavoriteFolder
from repo.models.content import Document
from repo.models.containers import Folder
from repo.models.people import Profile


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
