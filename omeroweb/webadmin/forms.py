#!/usr/bin/env python
# 
# 
# 
# Copyright (c) 2008 University of Dundee. 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# Author: Aleksandra Tarkowska <A(dot)Tarkowska(at)dundee(dot)ac(dot)uk>, 2008.
# 
# Version: 1.0
#

import re

from django.conf import settings
from django.db import models
from django import forms
from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.forms.widgets import HiddenInput

from custom_forms import GroupModelChoiceField, GroupModelMultipleChoiceField, ExperimenterModelChoiceField, ExperimenterModelMultipleChoiceField

from omeroweb.webadmin.models import Gateway

##################################################################
# Fields

class OmeNameField(forms.Field):
    def clean(self, value):
        omeName = value
        if not value:
            raise forms.ValidationError('This field is required.')
        if not self.is_valid_omeName(omeName):
            raise forms.ValidationError('%s is not a valid Omename.' % omeName)
        return omeName

    def is_valid_omeName(self, omeName):
        omeName_pattern = re.compile(r"(?:^|\s)[a-zA-Z0-9_.]") #TODO: PATTERN !!!!!!!
        return omeName_pattern.match(omeName) is not None


#################################################################
# Non-model Form

class LoginForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        g = Gateway.objects.all()
        try:
            if len(g) > 1:
                self.fields['server'] = forms.ModelChoiceField(g, empty_label=u"---------")
            else:
                self.fields['server'] = forms.ModelChoiceField(g, empty_label=None)
        except:
            self.fields['server'] = forms.ModelChoiceField(g, empty_label=u"---------")
        
        self.fields.keyOrder = ['server', 'username', 'password']
            
    #server = forms.ModelChoiceField(Gateway.objects.all(), empty_label=u"---------")
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'size':22}))
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'size':22}))


class ForgottonPasswordForm(forms.Form):
    
    server = forms.ModelChoiceField(Gateway.objects.all(), empty_label=u"---------")
    username = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'size':28}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':28}))


class ExperimenterForm(forms.Form):

    def __init__(self, name_check=False, email_check=False, *args, **kwargs):
        super(ExperimenterForm, self).__init__(*args, **kwargs)
        self.name_check=name_check
        self.email_check=email_check
        try:
            if kwargs['initial']['default_group']: pass
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['dgroups'], initial=kwargs['initial']['default_group'])
        except:
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['dgroups'])
        try:
            if kwargs['initial']['other_groups']: pass
            self.fields['other_groups'] = GroupModelMultipleChoiceField(queryset=kwargs['initial']['groups'], initial=kwargs['initial']['other_groups'], required=False, widget=forms.SelectMultiple(attrs={'size':7}))
        except:
            self.fields['other_groups'] = GroupModelMultipleChoiceField(queryset=kwargs['initial']['groups'], required=False, widget=forms.SelectMultiple(attrs={'size':7}))
        self.fields.keyOrder = ['omename', 'first_name', 'middle_name', 'last_name', 'email', 'institution', 'administrator', 'active', 'default_group', 'other_groups', 'password', 'confirmation']

    omename = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    first_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    middle_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)
    last_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':30}))
    institution = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)
    administrator = forms.CharField(widget=forms.CheckboxInput(), required=False)
    active = forms.CharField(widget=forms.CheckboxInput(), required=False)
    
    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'size':30}), required=False)
    confirmation = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'size':30}), required=False)
    
    def clean_omename(self):
        if self.name_check:
            raise forms.ValidationError('This omename already exist.')

    def clean_email(self):
        if self.email_check:
            raise forms.ValidationError('This email already exist.')
    
    def clean_confirmation(self):
        if self.cleaned_data.get('password') or self.cleaned_data.get('confirmation'):
            if len(self.cleaned_data.get('password')) < 3:
                raise forms.ValidationError('Password must be at least 3 letters long')
            if self.cleaned_data.get('password') != self.cleaned_data.get('confirmation'):
                raise forms.ValidationError('Passwords do not match')
            else:
                return self.cleaned_data.get('password')
            

class ExperimenterLdapForm(forms.Form):

    def __init__(self, name_check=False, email_check=False, *args, **kwargs):
        super(ExperimenterLdapForm, self).__init__(*args, **kwargs)
        self.name_check=name_check
        self.email_check=email_check
        try:
            if kwargs['initial']['default_group']: pass
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['dgroups'], initial=kwargs['initial']['default_group'])
        except:
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['dgroups'])
        try:
            if kwargs['initial']['other_groups']: pass
            self.fields['other_groups'] = GroupModelMultipleChoiceField(queryset=kwargs['initial']['groups'], initial=kwargs['initial']['other_groups'], required=False, widget=forms.SelectMultiple(attrs={'size':7}))
        except:
            self.fields['other_groups'] = GroupModelMultipleChoiceField(queryset=kwargs['initial']['groups'], required=False, widget=forms.SelectMultiple(attrs={'size':7}))
        self.fields.keyOrder = ['omename', 'first_name', 'middle_name', 'last_name', 'email', 'institution', 'administrator', 'active', 'default_group', 'other_groups']

    omename = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    first_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    middle_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)
    last_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':30}))
    institution = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)
    administrator = forms.CharField(widget=forms.CheckboxInput(), required=False)
    active = forms.CharField(widget=forms.CheckboxInput(), required=False)
    
    def clean_omename(self):
        if self.name_check:
            raise forms.ValidationError('This omename already exist.')
    
    def clean_email(self):
        if self.email_check:
            raise forms.ValidationError('This email already exist.')


class GroupForm(forms.Form):
    
    #PERMISSION_CHOICES = (
    #    ('0', 'Private (rw----)'),
    #    ('1', 'Group visible (rwr---)')
    #)
    
    def __init__(self, name_check=False, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)
        self.name_check=name_check
        try:
            if kwargs['initial']['owner']: pass
            self.fields['owner'] = ExperimenterModelChoiceField(queryset=kwargs['initial']['experimenters'], initial=kwargs['initial']['owner'])
        except:
            self.fields['owner'] = ExperimenterModelChoiceField(queryset=kwargs['initial']['experimenters'])
        #self.fields.keyOrder = ['name', 'description', 'owner', 'access_controll']
        self.fields.keyOrder = ['name', 'description', 'owner']

    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25}))
    description = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':25}), required=False)
    #access_controll = forms.ChoiceField(choices=PERMISSION_CHOICES, widget=forms.RadioSelect(), required=True)
    
    def clean_name(self):
        if self.name_check:
            raise forms.ValidationError('This name already exist.')


class ScriptForm(forms.Form):
    
    name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':51}))
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 50}))
    size = forms.CharField(label="size [B]", max_length=250, widget=forms.TextInput(attrs={'onfocus':'this.blur()', 'size':5}), required=False)


class MyAccountForm(forms.Form):
        
    def __init__(self, email_check=False, *args, **kwargs):
        super(MyAccountForm, self).__init__(*args, **kwargs)
        self.email_check=email_check
        try:
            if kwargs['initial']['default_group']: pass
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['groups'], initial=kwargs['initial']['default_group'], empty_label=None)
        except:
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['groups'], empty_label=None)
        self.fields.keyOrder = ['omename', 'first_name', 'middle_name', 'last_name', 'email', 'institution', 'default_group', 'password', 'confirmation']

    omename = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'onfocus':'this.blur()', 'size':30}))
    first_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    middle_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)
    last_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':30}))
    institution = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)

    password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'size':30}), required=False)
    confirmation = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={'size':30}), required=False)
    
    def clean_email(self):
        if self.email_check:
            raise forms.ValidationError('This email already exist.')
    
    def clean_confirmation(self):
        if self.cleaned_data.get('password') and self.cleaned_data.get('confirmation'):
            if len(self.cleaned_data.get('password')) < 3:
                raise forms.ValidationError('Password must be at least 3 letters long')
            if self.cleaned_data.get('password') != self.cleaned_data.get('confirmation'):
                raise forms.ValidationError('Passwords do not match')
            else:
                return self.cleaned_data.get('password')


class MyAccountLdapForm(forms.Form):

    def __init__(self, email_check=False, *args, **kwargs):
        super(MyAccountLdapForm, self).__init__(*args, **kwargs)
        self.email_check=email_check
        try:
            if kwargs['initial']['default_group']: pass
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['groups'], initial=kwargs['initial']['default_group'], empty_label=None)
        except:
            self.fields['default_group'] = GroupModelChoiceField(queryset=kwargs['initial']['groups'], empty_label=None)
        self.fields.keyOrder = ['omename', 'first_name', 'middle_name', 'last_name', 'email', 'institution', 'default_group']

    omename = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'onfocus':'this.blur()', 'size':30}))
    first_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    middle_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)
    last_name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'size':30}))
    institution = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), required=False)

    def clean_email(self):
        if self.email_check:
            raise forms.ValidationError('This email already exist.')


class ContainedExperimentersForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ContainedExperimentersForm, self).__init__(*args, **kwargs)
        self.fields['members'] = ExperimenterModelMultipleChoiceField(queryset=kwargs['initial']['members'], required=False, widget=forms.SelectMultiple(attrs={'size':25}))
        self.fields['available'] = ExperimenterModelMultipleChoiceField(queryset=kwargs['initial']['available'], required=False, widget=forms.SelectMultiple(attrs={'size':25}))
        self.fields.keyOrder = ['members', 'available']


class UploadPhotoForm(forms.Form):
    
    photo = forms.FileField(required=False)

    def clean_photo(self):
        if self.cleaned_data.get('photo') is None:
            raise forms.ValidationError('This field is required.')
        if not self.cleaned_data.get('photo').content_type.startswith("image"):
            raise forms.ValidationError('Only images (JPEG, GIF, PNG) acepted.')
        if self.cleaned_data.get('photo').size > 204800:
            raise forms.ValidationError('Photo size file cannot be greater them 200KB.')


class EnumerationEntry(forms.Form):
    
    new_entry = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}))


class EnumerationEntries(forms.Form):
    
    def __init__(self, entries, *args, **kwargs):
        super(EnumerationEntries, self).__init__(*args, **kwargs)        
        for i,e in enumerate(entries):
            try:
                if kwargs['initial']['entries']:
                    self.fields[str(e.id)] = forms.CharField(max_length=250, initial=e.value, widget=forms.TextInput(attrs={'size':30}), label=i+1)
                else:
                    self.fields[str(e.id)] = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), label=i+1)
            except:
                self.fields[str(e.id)] = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':30}), label=i+1)
                    
        self.fields.keyOrder = [str(k) for k in self.fields.keys()]
    