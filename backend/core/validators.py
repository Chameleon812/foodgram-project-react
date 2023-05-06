from string import hexdigits

from django.core.exceptions import ValidationError


def check_user_info(queryset, user):
    if user.is_anonymous:
        return False
    return queryset.filter(pk=user.pk).exists()


def validate_hex(color):
    color = color.strip(' #')
    if len(color) != 6:
        raise ValidationError(
            'The specified hex color is not the correct length'
        )
    if not set(color).issubset(hexdigits):
        raise ValidationError(
            'The specified hex color does not exist'
        )
    return '#' + color.upper()
