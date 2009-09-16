import re
from itertools import chain

from django import forms
from django.forms.widgets import SelectMultiple, CheckboxInput, MultipleHiddenInput
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe

from django.forms.fields import Field, EMPTY_VALUES
from django.forms.widgets import Select
from django.forms import ModelChoiceField, ValidationError
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_unicode

##################################################################
# Fields

class MultiEmailField(forms.Field):
    def clean(self, value):
        if not value:
            raise forms.ValidationError('No email.')
        if value.count(' ') > 0:
            raise forms.ValidationError('Use only separator ";". Remove every spaces.')
        emails = value.split(';')
        for email in emails:
            if not self.is_valid_email(email):
                raise forms.ValidationError('%s is not a valid e-mail address. Use separator ";"' % email)
        return emails

    def is_valid_email(self, email):
        email_pat = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)
        return email_pat.match(email) is not None

class UrlField(forms.Field):
    def clean(self, value):
        if not value:
            raise forms.ValidationError('No url.')
        if not self.is_valid_url(value):
            raise forms.ValidationError('%s is not a valid url' % value)
        return value
    
    def is_valid_url(self, url):
        url_pat = re_http = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',re.IGNORECASE)
        return url_pat.match(url) is not None

##################################################################
# Metadata queryset iterator for group form

class MetadataQuerySetIterator(object):
    def __init__(self, queryset, empty_label, cache_choices):
        self.queryset = queryset
        self.empty_label = empty_label
        self.cache_choices = cache_choices

    def __iter__(self):
        if self.empty_label is not None:
            yield (u"", self.empty_label)
        for obj in self.queryset:
            yield (obj.value, smart_unicode(obj.value))
        # Clear the QuerySet cache if required.
        #if not self.cache_choices:
            #self.queryset._result_cache = None

class MetadataModelChoiceField(ModelChoiceField):

    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices
        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh QuerySetIterator that has not
        # been consumed. Note that we're instantiating a new QuerySetIterator
        # *each* time _get_choices() is called (and, thus, each time
        # self.choices is accessed) so that we can ensure the QuerySet has not
        # been consumed.
        return MetadataQuerySetIterator(self.queryset, self.empty_label,
                                self.cache_choices)

    def _set_choices(self, value):
        # This method is copied from ChoiceField._set_choices(). It's necessary
        # because property() doesn't allow a subclass to overwrite only
        # _get_choices without implementing _set_choices.
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def clean(self, value):
        Field.clean(self, value)
        if value in EMPTY_VALUES:
            return None
        res = False
        for q in self.queryset:
            if long(value) == q.id:
                res = True
        if not res:
            raise ValidationError(self.error_messages['invalid_choice'])
        return value

class AnnotationQuerySetIterator(object):
    
    def __init__(self, queryset, empty_label, cache_choices):
        self.queryset = queryset
        self.empty_label = empty_label
        self.cache_choices = cache_choices

    def __iter__(self):
        if self.empty_label is not None:
            yield (u"", self.empty_label)
        for obj in self.queryset:
            textValue = None
            from omero_model_FileAnnotationI import FileAnnotationI
            from omero_model_TagAnnotationI import TagAnnotationI
            if isinstance(obj._obj, FileAnnotationI):
                textValue = obj.file.name.val
            elif isinstance(obj._obj, TagAnnotationI):
                if obj.textValue is not None:
                    if obj.description is not None and obj.description is not "":
                        textValue = "%s (%s)" % ((obj.textValue[:45]+"...", obj.textValue)[ len(obj.textValue)<45 ], \
                            (obj.description[:25]+"...", obj.description)[ len(obj.description)<25 ])
                    else:
                        textValue = obj.textValue
            else:
                textValue = obj.textValue
            
            l = len(textValue)
            if l > 80:
                textValue = "%s..." % textValue[:80]
            
            oid = obj.id
            yield (oid, smart_unicode(textValue))
        # Clear the QuerySet cache if required.
        #if not self.cache_choices:
            #self.queryset._result_cache = None

class AnnotationModelChoiceField(ModelChoiceField):
    
    def _get_choices(self):
        # If self._choices is set, then somebody must have manually set
        # the property self.choices. In this case, just return self._choices.
        if hasattr(self, '_choices'):
            return self._choices
        # Otherwise, execute the QuerySet in self.queryset to determine the
        # choices dynamically. Return a fresh QuerySetIterator that has not
        # been consumed. Note that we're instantiating a new QuerySetIterator
        # *each* time _get_choices() is called (and, thus, each time
        # self.choices is accessed) so that we can ensure the QuerySet has not
        # been consumed.
        return AnnotationQuerySetIterator(self.queryset, self.empty_label,
                                self.cache_choices)

    def _set_choices(self, value):
        # This method is copied from ChoiceField._set_choices(). It's necessary
        # because property() doesn't allow a subclass to overwrite only
        # _get_choices without implementing _set_choices.
        self._choices = self.widget.choices = list(value)

    choices = property(_get_choices, _set_choices)

    def clean(self, value):
        Field.clean(self, value)
        if value in EMPTY_VALUES:
            return None
        res = False
        for q in self.queryset:
            if long(value) == q.id:
                res = True
        if not res:
            raise ValidationError(self.error_messages['invalid_choice'])
        return value

class AnnotationModelMultipleChoiceField(AnnotationModelChoiceField):
    """A MultipleChoiceField whose choices are a model QuerySet."""
    hidden_widget = MultipleHiddenInput
    default_error_messages = {
        'list': _(u'Enter a list of values.'),
        'invalid_choice': _(u'Select a valid choice. That choice is not one of the'
                            u' available choices.'),
    }
    def __init__(self, queryset, cache_choices=False, required=True,
                 widget=SelectMultiple, label=None, initial=None,
                 help_text=None, *args, **kwargs):
        super(AnnotationModelMultipleChoiceField, self).__init__(queryset, None,
            cache_choices, required, widget, label, initial, help_text,
            *args, **kwargs)
    
    def clean(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])
        final_values = []
        for val in value:
            try:
                long(val)
            except:
                raise ValidationError(self.error_messages['invalid_choice'])
            else:
                res = False
                for q in self.queryset:
                    if long(val) == q.id:
                        res = True
                if not res:
                    raise ValidationError(self.error_messages['invalid_choice'])
                else:
                    final_values.append(val)
        return final_values
