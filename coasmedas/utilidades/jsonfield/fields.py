from django.core.exceptions import ValidationError
from django.db import models, DatabaseError, transaction
import json
from django.utils.translation import ugettext_lazy as _

from decimal import Decimal
import datetime, pyodbc

from .utils import default
from .widgets import JSONWidget
from .forms import JSONFormField

class JSONField(models.Field):
    """
    A field that will ensure the data entered into it is valid JSON.
    """
    # __metaclass__ = models.SubfieldBase
    default_error_messages = {
        'invalid': _(u"'%s' is not a valid JSON string.")
    }
    description = "JSON object"
    
    def __init__(self, *args, **kwargs):
        if not kwargs.get('null', False):
            kwargs['default'] = kwargs.get('default', {})
        super(JSONField, self).__init__(*args, **kwargs)
        if 'default' in kwargs:
            if callable(self.default):
                self.validate(self.default(), None)
            else:
                self.validate(self.default, None)
        
    def formfield(self, **kwargs):
        defaults = {
            'form_class': JSONFormField,
            'widget': JSONWidget
        }
        defaults.update(**kwargs)
        return super(JSONField, self).formfield(**defaults)
    
    def validate(self, value, model_instance):
        if not self.null and value is None:
            raise ValidationError(self.error_messages['null'])
        try:
            self.get_prep_value(value)
        except Exception as e:
            raise ValidationError(self.error_messages['invalid'] % value)

    def get_default(self):
        if self.has_default():
            if callable(self.default):
                return self.default()
            return self.default
        return super(JSONField, self).get_default()

    def get_internal_type(self):
        return 'TextField'
    
    def db_type(self, connection):
        # Test to see if we support JSON
        cursor = connection.cursor()
        try:
            sid = transaction.savepoint()
            cursor.execute('SELECT \'{"a":"json object"}\'::json;')
        except (DatabaseError, pyodbc.ProgrammingError):
            transaction.savepoint_rollback(sid)
            return 'text'
        else:
            return 'json'
    
    def to_python(self, value):
        if isinstance(value, basestring):
            if value == "":
                if self.null:
                    return None
                if self.blank:
                    return ""
            try:
                value = json.loads(value)
            except ValueError:
                msg = self.error_messages['invalid'] % str(value)
                raise ValidationError(msg)
        # TODO: Look for date/time/datetime objects within the structure?
        return value

    def get_db_prep_value(self, value, connection=None, prepared=None):
        return self.get_prep_value(value)
    
    def get_prep_value(self, value):
        if value is None:
            if not self.null and self.blank:
                return ""
            return None
        return json.dumps(value, default=default)
    
    def get_prep_lookup(self, lookup_type, value):
        if lookup_type in ["exact", "iexact"]:
            return self.to_python(self.get_prep_value(value))
        if lookup_type == "in":
            return [self.to_python(self.get_prep_value(v)) for v in value]
        if lookup_type == "isnull":
            return value
        if lookup_type in ["contains", "icontains"]:
            if isinstance(value, (list, tuple)):
                raise TypeError("Lookup type %r not supported with argument of %s" % (
                    lookup_type, type(value).__name__
                ))
                # Need a way co combine the values with '%', but don't escape that.
                return self.get_prep_value(value)[1:-1].replace(', ', r'%')
            if isinstance(value, dict):
                return self.get_prep_value(value)[1:-1]
            return self.to_python(self.get_prep_value(value))
        raise TypeError('Lookup type %r not supported' % lookup_type)

    def value_to_string(self, obj):
        return self._get_val_from_obj(obj)

class TypedJSONField(JSONField):
    """
    
    """
    def __init__(self, *args, **kwargs):
        self.json_required_fields = kwargs.pop('required_fields', {})
        self.json_validators = kwargs.pop('validators', [])
        
        super(TypedJSONField, self).__init__(*args, **kwargs)
    
    def cast_required_fields(self, obj):
        if not obj:
            return
        for field_name, field_type in self.json_required_fields.items():
            obj[field_name] = field_type.to_python(obj[field_name])
        
    def to_python(self, value):
        value = super(TypedJSONField, self).to_python(value)
        
        if isinstance(value, list):
            for item in value:
                self.cast_required_fields(item)
        else:
            self.cast_required_fields(value)
        
        return value
    
    def validate(self, value, model_instance):
        super(TypedJSONField, self).validate(value, model_instance)
        
        for v in self.json_validators:
            if isinstance(value, list):
                for item in value:
                    v(item)
            else:
                v(value)
    
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^jsonfield\.fields\.JSONField'])
    add_introspection_rules([], ['^jsonfield\.fields\.TypedJSONField'])
except ImportError:
    pass
