from django import forms
import json

from .widgets import JSONWidget


class JSONFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            kwargs['widget'] = JSONWidget
        super(JSONFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """
        The default is to have a TextField, and we will decode the string
        that comes back from this. However, another use of this field is
        to store a list of values, and use these in a MultipleSelect
        widget. So, if we have an object that isn't a string, then for now
        we will assume that is where it has come from.
        """
        if not value:
            return value
        if isinstance(value, basestring):
            try:
                return json.loads(value)
            except Exception as exc:
                raise forms.ValidationError(
                    u'JSON decode error: %s' % (unicode(exc),)
                )
        else:
            return value
