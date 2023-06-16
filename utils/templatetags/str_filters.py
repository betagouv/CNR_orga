"""
https://docs.djangoproject.com/en/dev/howto/custom-template-tags/
"""
from django import template


register = template.Library()


@register.filter(is_safe=False)
def pluralizefr(value, arg="s"):
    """
    Return a plural suffix if the value is greater than 1
    NB : the native django pluralize filter returns the plural suffix for value==0
    """
    try:
        return arg if float(value) > 1 else ""
    except ValueError:  # Invalid string that's not a number.
        pass
    except TypeError:  # Value isn't a string or a number; maybe it's a list?
        try:
            return arg if len(value) > 1 else ""
        except TypeError:  # len() of unsized object.
            pass
    return ""
