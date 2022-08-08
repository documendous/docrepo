import logging
from django import template


register = template.Library()


@register.filter(name="remove_str")
def remove_str(var, args):
    LOGGER = logging.getLogger(__name__)
    replaced_str = var
    for each in args.split(","):
        LOGGER.debug('Looking to remove string "{}" from string "{}"'.format(each, var))
        replaced_str = replaced_str.replace(each, "")
    LOGGER.debug("Finished and returning: {}".format(replaced_str))
    return replaced_str
