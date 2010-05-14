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

import datetime
import time

from django import forms
from django.forms.widgets import Textarea
from django.forms.widgets import HiddenInput
from django.core.urlresolvers import reverse

from custom_forms import UrlField, MetadataModelChoiceField, \
                        AnnotationModelMultipleChoiceField
from omeroweb.webadmin.custom_forms import ExperimenterModelChoiceField, \
                        ExperimenterModelMultipleChoiceField, \
                        GroupModelMultipleChoiceField, GroupModelChoiceField
                        
##################################################################
# Static values

# TODO: change to reverse
help_button = "/appmedia/omeroweb/images/help16.png"

help_wiki = '<span id="markup" title="Markups - <small>If you\'d like to include URL please type:<br/><b>http://www.openmicroscopy.org.uk/</b></small>"><img src="%s" /></span>' % help_button

help_wiki_c = '<span id="markup_c" title="Markups - <small>If you\'d like to include URL please type:<br/><b>http://www.openmicroscopy.org.uk/</b></small>"><img src="%s" /></span>' % help_button

help_enable = '<span id="enable" title="Enable/Disable - <small>This option allows the owner to keep the access control of the share.</small>"><img src="%s" /></span>' % help_button

help_expire = '<span id="expire" title="Expire date - <small>This date defines when share will stop being available. Date format: YY-MM-DD.</small>"><img src="%s" /></span>' % help_button

#################################################################
# Non-model Form

class ShareForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(ShareForm, self).__init__(*args, **kwargs)
        
        try:
            if kwargs['initial']['shareMembers']: pass
            self.fields['members'] = ExperimenterModelMultipleChoiceField(queryset=kwargs['initial']['experimenters'], initial=kwargs['initial']['shareMembers'], widget=forms.SelectMultiple(attrs={'size':5}))
        except:
            self.fields['members'] = ExperimenterModelMultipleChoiceField(queryset=kwargs['initial']['experimenters'], widget=forms.SelectMultiple(attrs={'size':5}))
        self.fields.keyOrder = ['message', 'expiration', 'enable', 'members']#, 'guests']
    
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 39}), help_text=help_wiki_c) 
    expiration = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':20}), label="Expire date", help_text=help_expire, required=False)
    enable = forms.CharField(widget=forms.CheckboxInput(attrs={'size':1}), required=False, help_text=help_enable)
    #guests = MultiEmailField(required=False, widget=forms.TextInput(attrs={'size':75}))

    def clean_expiration(self):
        da = self.cleaned_data['expiration'].encode('utf-8')
        if da is not None and da != "":
            d = da.rsplit("-")
            # only for python 2.5
            # date = datetime.datetime.strptime(("%s-%s-%s" % (d[0],d[1],d[2])), "%Y-%m-%d")
            try:
                date = datetime.datetime(*(time.strptime(("%s-%s-%s 23:59:59" % (d[0],d[1],d[2])), "%Y-%m-%d %H:%M:%S")[0:6]))
            except:
                raise forms.ValidationError('Date is in the wrong format. YY-MM-DD')
            if time.mktime(date.timetuple()) <= time.time():
                raise forms.ValidationError('Expire date must be in the future.')

class BasketShareForm(ShareForm):
    
    def __init__(self, *args, **kwargs):
        super(BasketShareForm, self).__init__(*args, **kwargs)
        
        try:
            self.fields['image'] = GroupModelMultipleChoiceField(queryset=kwargs['initial']['images'], initial=kwargs['initial']['selected'], widget=forms.SelectMultiple(attrs={'size':10}))
        except:
            self.fields['image'] = GroupModelMultipleChoiceField(queryset=kwargs['initial']['images'], widget=forms.SelectMultiple(attrs={'size':10}))


class ShareCommentForm(forms.Form):

    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'cols': 39}), help_text=help_wiki_c)
    
class ContainerForm(forms.Form):
    
    name = forms.CharField(max_length=250, widget=forms.TextInput(attrs={'size':45}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 39}), required=False, help_text=help_wiki)
    
class CommentAnnotationForm(forms.Form):
    
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 39}))

class TagFilterForm(forms.Form):
    
    tag = forms.CharField(widget=forms.TextInput(attrs={'size':36}), required=False)

class TagAnnotationForm(forms.Form):
    
    tag = forms.CharField(widget=forms.TextInput(attrs={'size':36}))
    description = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 31}), required=False, label="Desc")

class TagListForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(TagListForm, self).__init__(*args, **kwargs)
        self.fields['tags'] = AnnotationModelMultipleChoiceField(queryset=kwargs['initial']['tags'], widget=forms.SelectMultiple(attrs={'size':6, 'class':'existing'}))
        self.fields.keyOrder = ['tags']

class CommentListForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(CommentListForm, self).__init__(*args, **kwargs)
        self.fields['comments'] = AnnotationModelMultipleChoiceField(queryset=kwargs['initial']['comments'], widget=forms.SelectMultiple(attrs={'size':6, 'class':'existing'}))
        self.fields.keyOrder = ['comments']

class UrlListForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(UrlListForm, self).__init__(*args, **kwargs)
        self.fields['urls'] = AnnotationModelMultipleChoiceField(queryset=kwargs['initial']['urls'], widget=forms.SelectMultiple(attrs={'size':6, 'class':'existing'}))
        self.fields.keyOrder = ['urls']

class FileListForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(FileListForm, self).__init__(*args, **kwargs)
        self.fields['files'] = AnnotationModelMultipleChoiceField(queryset=kwargs['initial']['files'], widget=forms.SelectMultiple(attrs={'size':6, 'class':'existing'}))
        self.fields.keyOrder = ['files']

class UploadFileForm(forms.Form):
    annotation_file  = forms.FileField(required=False)
    
    def clean_annotation_file(self):
        if self.cleaned_data['annotation_file'] is None:
            raise forms.ValidationError('This field is required.')

class UsersForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(UsersForm, self).__init__(*args, **kwargs)
        try:
            empty_label = kwargs['initial']['empty_label']
        except:
            empty_label='*Mydata'
        try:
            menu = kwargs['initial']['menu']
        except:
            menu = 'userdata'
        try:
            if kwargs['initial']['user']: pass
            self.fields['experimenter'] = ExperimenterModelChoiceField(queryset=kwargs['initial']['users'], initial=kwargs['initial']['user'], widget=forms.Select(attrs={'onchange':'window.location.href=\''+reverse(viewname="load_template", args=[menu])+'?experimenter=\'+this.options[this.selectedIndex].value'}), required=False, empty_label=empty_label)
        except:
            self.fields['experimenter'] = ExperimenterModelChoiceField(queryset=kwargs['initial']['users'], widget=forms.Select(attrs={'onchange':'window.location.href=\''+reverse(viewname="load_template", args=[menu])+'?experimenter=\'+this.options[this.selectedIndex].value'}), required=False, empty_label=empty_label)
        self.fields.keyOrder = ['experimenter']

class ActiveGroupForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ActiveGroupForm, self).__init__(*args, **kwargs)
        try:
            self.fields['active_group'] = GroupModelChoiceField(queryset=kwargs['initial']['mygroups'], initial=kwargs['initial']['activeGroup'], empty_label=None, widget=forms.Select(attrs={'onchange':'window.location.href=\''+reverse(viewname="change_active_group")+'?url='+kwargs['initial']['url']+'&active_group=\'+this.options[this.selectedIndex].value'})) 
        except:
            self.fields['active_group'] = GroupModelChoiceField(queryset=kwargs['initial']['mygroups'], initial=kwargs['initial']['activeGroup'], empty_label=None, widget=forms.Select(attrs={'onchange':'window.location.href=\''+reverse(viewname="change_active_group")+'?active_group=\'+this.options[this.selectedIndex].value'})) 
        self.fields.keyOrder = ['active_group']

class HistoryTypeForm(forms.Form):
    HISTORY_CHOICES = (
        ('all', '---------'),
        ('project', 'Projects'),
        ('dataset', 'Datasets'),
        ('image', 'Images'),
        #('renderdef', 'Views'),
    )
    
    data_type = forms.ChoiceField(choices=HISTORY_CHOICES,  widget=forms.Select(attrs={'onchange':'window.location.href=\'?history_type=\'+this.options[this.selectedIndex].value'}))


class WellIndexForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(WellIndexForm, self).__init__(*args, **kwargs)
        choices = [(str(i), "Field#%i" % (i+1)) for i in range(0, kwargs['initial']['range'])]
        self.fields['index'] = forms.ChoiceField(choices=tuple(choices),  widget=forms.Select(attrs={'onchange':'changeIndex(this.options[this.selectedIndex].value);'}))
        
        self.fields.keyOrder = ['index']

###############################
# METADATA FORMS
class MetadataChannelForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataChannelForm, self).__init__(*args, **kwargs)
        
        # Logical channel
        
        # Name
        try:
            if kwargs['initial']['logicalChannel'] is not None:
                self.fields['name'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].name, required=False)
            else:
                self.fields['name'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), required=False)
            self.fields['name'].widget.attrs['disabled'] = True 
            self.fields['name'].widget.attrs['class'] = 'disable'
        except:
            self.fields['name'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['name'].widget.attrs['disabled'] = True 
            self.fields['name'].widget.attrs['class'] = 'disabled'
        
        # excitationWave
        try:
            if kwargs['initial']['logicalChannel'] is not None:
                self.fields['excitationWave'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].excitationWave, label="Excitation", required=False)
            else:
                self.fields['excitationWave'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), label="Excitation", required=False)
            self.fields['excitationWave'].widget.attrs['disabled'] = True 
            self.fields['excitationWave'].widget.attrs['class'] = 'disable'
        except:
            self.fields['excitationWave'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Excitation", required=False)
            self.fields['excitationWave'].widget.attrs['disabled'] = True 
            self.fields['excitationWave'].widget.attrs['class'] = 'disabled'
        
        # emissionWave
        try:
            if kwargs['initial']['logicalChannel'] is not None:
                self.fields['emissionWave'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].emissionWave, label="Emission", required=False)
            else:
                self.fields['emissionWave'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), label="Emission", required=False)
            self.fields['emissionWave'].widget.attrs['disabled'] = True 
            self.fields['emissionWave'].widget.attrs['class'] = 'disable'
        except:
            self.fields['emissionWave'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Emission", required=False)
            self.fields['emissionWave'].widget.attrs['disabled'] = True 
            self.fields['emissionWave'].widget.attrs['class'] = 'disabled'
        
        # ndFilter
        try:
            if kwargs['initial']['logicalChannel'] is not None:
                self.fields['ndFilter'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].ndFilter, label="ND filter [%]", required=False)
            else:
                self.fields['ndFilter'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), label="ND filter [%]", required=False)
            self.fields['ndFilter'].widget.attrs['disabled'] = True 
            self.fields['ndFilter'].widget.attrs['class'] = 'disable'
        except:
            self.fields['ndFilter'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="ND filter [%]", required=False)
            self.fields['ndFilter'].widget.attrs['disabled'] = True 
            self.fields['ndFilter'].widget.attrs['class'] = 'disabled'
        
        # pinHoleSize
        try:
            if kwargs['initial']['logicalChannel'] is not None:
                self.fields['pinHoleSize'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].pinHoleSize, label="Pin hole size", required=False)
            else:
                self.fields['pinHoleSize'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), label="Pin hole size", required=False)
            self.fields['pinHoleSize'].widget.attrs['disabled'] = True 
            self.fields['pinHoleSize'].widget.attrs['class'] = 'disable'
        except:
            self.fields['pinHoleSize'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Pin hole size", required=False)
            self.fields['pinHoleSize'].widget.attrs['disabled'] = True 
            self.fields['pinHoleSize'].widget.attrs['class'] = 'disabled'
        
        # fluor
        try:
            if kwargs['initial']['logicalChannel'] is not None:
                self.fields['fluor'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].fluor, required=False)
            else:
                self.fields['fluor'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), required=False)
            self.fields['fluor'].widget.attrs['disabled'] = True 
            self.fields['fluor'].widget.attrs['class'] = 'disable'
        except:
            self.fields['fluor'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['fluor'].widget.attrs['disabled'] = True 
            self.fields['fluor'].widget.attrs['class'] = 'disabled'
        
        # Illumination
        try:
            if kwargs['initial']['logicalChannel'].illumination is not None:
                self.fields['illumination'] = MetadataModelChoiceField(queryset=kwargs['initial']['illuminations'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'illumination\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['logicalChannel'].getIllumination().value, required=False) 
            else:
                self.fields['illumination'] = MetadataModelChoiceField(queryset=kwargs['initial']['illuminations'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'illumination\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['illumination'].widget.attrs['disabled'] = True 
            self.fields['illumination'].widget.attrs['class'] = 'disable'
        except:
            self.fields['illumination'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['illumination'].widget.attrs['disabled'] = True 
            self.fields['illumination'].widget.attrs['class'] = 'disabled'
        
        # contrastMethods
        try:
            if kwargs['initial']['logicalChannel'].contrastMethod is not None:
                self.fields['contrastMethod'] = MetadataModelChoiceField(queryset=kwargs['initial']['contrastMethods'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'contrastMethod\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['logicalChannel'].getContrastMethod().value, label="Contrast method", required=False) 
            else:
                self.fields['contrastMethod'] = MetadataModelChoiceField(queryset=kwargs['initial']['contrastMethods'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'contrastMethod\', this.options[this.selectedIndex].value);'}), label="Contrast method", required=False) 
            self.fields['contrastMethod'].widget.attrs['disabled'] = True 
            self.fields['contrastMethod'].widget.attrs['class'] = 'disable'
        except:
            self.fields['contrastMethod'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Contrast method", required=False)
            self.fields['contrastMethod'].widget.attrs['disabled'] = True 
            self.fields['contrastMethod'].widget.attrs['class'] = 'disabled'
        
        # Illumination
        try:
            if kwargs['initial']['logicalChannel'].mode is not None:
                self.fields['mode'] = MetadataModelChoiceField(queryset=kwargs['initial']['modes'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'mode\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['logicalChannel'].getMode().value, required=False) 
            else:
                self.fields['mode'] = MetadataModelChoiceField(queryset=kwargs['initial']['modes'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'mode\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['mode'].widget.attrs['disabled'] = True 
            self.fields['mode'].widget.attrs['class'] = 'disable'
        except:
            self.fields['mode'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['mode'].widget.attrs['disabled'] = True 
            self.fields['mode'].widget.attrs['class'] = 'disabled'
        
        # pockelCellSetting
        try:
            if kwargs['initial']['logicalChannel'].pockelCellSetting is not None:
                self.fields['pockelCellSetting'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), initial=kwargs['initial']['logicalChannel'].pockelCellSetting, label="Pockel cell", required=False)
            else:
                self.fields['pockelCellSetting'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalChannel'].id)+', \'name\', this.value);'}), label="Pockel cell", required=False)
            self.fields['pockelCellSetting'].widget.attrs['disabled'] = True 
            self.fields['pockelCellSetting'].widget.attrs['class'] = 'disable'
        except:
            self.fields['pockelCellSetting'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Pockel cell" ,required=False)
            self.fields['pockelCellSetting'].widget.attrs['disabled'] = True 
            self.fields['pockelCellSetting'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['name', 'excitationWave', 'emissionWave', 'ndFilter', 'pinHoleSize', 'fluor', 'illumination', 'contrastMethod', 'mode', 'pockelCellSetting'] 


class MetadataDichroicForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataDichroicForm, self).__init__(*args, **kwargs)
    
        # Manufacturer
        try:
            if kwargs['initial']['logicalchannel'].getDichroic().manufacturer is not None:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalchannel'].id)+', \'manufacturer\', this.value);'}), initial=kwargs['initial']['logicalchannel'].getDichroic().manufacturer, required=False)
            else:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalchannel'].id)+', \'manufacturer\', this.value);'}), required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disable'
        except:
            self.fields['manufacturer'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disabled'

        # Model
        try:
            if kwargs['initial']['logicalchannel'].getDichroic().model is not None:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalchannel'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['logicalchannel'].getDichroic().model, required=False)
            else:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalchannel'].id)+', \'model\', this.value);'}), required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disable'
        except:
            self.fields['model'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disabled'
        
        # Lot number
        try:
            if kwargs['initial']['logicalchannel'].getDichroic().lotNumber is not None:
                self.fields['lotNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalchannel'].getDichroic().lotNumber)+', \'lotNumber\', this.value);'}), initial=kwargs['initial']['logicalchannel'].getDichroic().lotNumber, label="Lot number", required=False)
            else:
                self.fields['lotNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['logicalchannel'].getDichroic().lotNumber)+', \'lotNumber\', this.value);'}), label="Lot number", required=False)
            self.fields['lotNumber'].widget.attrs['disabled'] = True 
            self.fields['lotNumber'].widget.attrs['class'] = 'disable'
        except:
            self.fields['lotNumber'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Lot number", required=False)
            self.fields['lotNumber'].widget.attrs['disabled'] = True 
            self.fields['lotNumber'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['manufacturer', 'model', 'lotNumber'] 


class MetadataMicroscopeForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataMicroscopeForm, self).__init__(*args, **kwargs)
    
        # Model
        try:
            if kwargs['initial']['microscope'].model is not None:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['microscope'].model, required=False)
            else:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'model\', this.value);'}), required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disable'
        except:
            self.fields['model'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disabled'
        
        # Manufacturer
        try:
            if kwargs['initial']['microscope'].manufacturer is not None:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'manufacturer\', this.value);'}), initial=kwargs['initial']['microscope'].manufacturer, required=False)
            else:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'manufacturer\', this.value);'}), required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disable'
        except:
            self.fields['manufacturer'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disabled'
        
        # Serial number
        try:
            if kwargs['initial']['microscope'].serialNumber is not None:
                self.fields['serialNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'lotNumber\', this.value);'}), initial=kwargs['initial']['microscope'].serialNumber, label="Serial number", required=False)
            else:
                self.fields['serialNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'lotNumber\', this.value);'}), label="Serial number", required=False)
            self.fields['serialNumber'].widget.attrs['disabled'] = True 
            self.fields['serialNumber'].widget.attrs['class'] = 'disable'
        except:
            self.fields['serialNumber'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Serial number", required=False)
            self.fields['serialNumber'].widget.attrs['disabled'] = True 
            self.fields['serialNumber'].widget.attrs['class'] = 'disabled'
        
        # Type
        try:
            if kwargs['initial']['microscope'].type is not None:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['microscopeTypes'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'medium\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['microscope'].type, required=False) 
            else:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['microscopeTypes'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['microscope'].id)+', \'medium\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disable'
        except:
            self.fields['type'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['model', 'manufacturer', 'serialNumber', 'type']


class MetadataObjectiveForm(forms.Form):
    
    BOOLEAN_CHOICES = (
        ('', '---------'),
        ('True', 'True'),
        ('False', 'False'),
    )
    
    def __init__(self, *args, **kwargs):
        super(MetadataObjectiveForm, self).__init__(*args, **kwargs)
        
        # Objective Settings
        
        # Correction Collar
        try:
            if kwargs['initial']['objectiveSettings'].correctionCollar is not None:
                self.fields['correctionCollar'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'correctionCollar\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].correctionCollar, label="Correction collar", required=False)
            else:
                self.fields['correctionCollar'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'correctionCollar\', this.value);'}), label="Correction collar", required=False)
            self.fields['correctionCollar'].widget.attrs['disabled'] = True 
            self.fields['correctionCollar'].widget.attrs['class'] = 'disable'
        except:
            self.fields['correctionCollar'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Correction collar", required=False)
            self.fields['correctionCollar'].widget.attrs['disabled'] = True 
            self.fields['correctionCollar'].widget.attrs['class'] = 'disabled'
        
        # Medium
        try:
            if kwargs['initial']['objectiveSettings'].medium is not None:
                self.fields['medium'] = MetadataModelChoiceField(queryset=kwargs['initial']['mediums'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'medium\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['objectiveSettings'].getMedium().value, required=False) 
            else:
                self.fields['medium'] = MetadataModelChoiceField(queryset=kwargs['initial']['mediums'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'medium\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['medium'].widget.attrs['disabled'] = True 
            self.fields['medium'].widget.attrs['class'] = 'disable'
        except:
            self.fields['medium'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['medium'].widget.attrs['disabled'] = True 
            self.fields['medium'].widget.attrs['class'] = 'disabled'
        
        # Refractive Index
        try:
            if kwargs['initial']['objectiveSettings'].refractiveIndex is not None:
                self.fields['refractiveIndex'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'refractiveIndex\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].refractiveIndex, label="Refractive index", required=False)
            else:
                self.fields['refractiveIndex'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'refractiveIndex\', this.value);'}), label="Refractive index", required=False)
            self.fields['refractiveIndex'].widget.attrs['disabled'] = True 
            self.fields['refractiveIndex'].widget.attrs['class'] = 'disable'
        except:
            self.fields['refractiveIndex'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Refractive index", required=False)
            self.fields['refractiveIndex'].widget.attrs['disabled'] = True 
            self.fields['refractiveIndex'].widget.attrs['class'] = 'disabled'
        
        # Objective
        
        # Model
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().model is not None:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().model, required=False)
            else:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'model\', this.value);'}), required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disable'
        except:
            self.fields['model'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disabled'
        
        # Manufacturer
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().manufacturer is not None:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'manufacturer\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().manufacturer, required=False)
            else:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'manufacturer\', this.value);'}), required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disable'
        except:
            self.fields['manufacturer'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disabled'
        
        # Serial Number
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().serialNumber is not None:
                self.fields['serialNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'serialNumber\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().serialNumber, label="Serial number", required=False)
            else:
                self.fields['serialNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'serialNumber\', this.value);'}), label="Serial number", required=False)
            self.fields['serialNumber'].widget.attrs['disabled'] = True 
            self.fields['serialNumber'].widget.attrs['class'] = 'disable'
        except:
            self.fields['serialNumber'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Serial number", required=False)
            self.fields['serialNumber'].widget.attrs['disabled'] = True 
            self.fields['serialNumber'].widget.attrs['class'] = 'disabled'
        
        # Nominal Magnification
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().nominalMagnification is not None:
                self.fields['nominalMagnification'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'nominalMagnification\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().nominalMagnification, label="Nominal magnification", required=False)
            else:
                self.fields['nominalMagnification'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'nominalMagnification\', this.value);'}), label="Nominal magnification", required=False)
            self.fields['nominalMagnification'].widget.attrs['disabled'] = True 
            self.fields['nominalMagnification'].widget.attrs['class'] = 'disable'
        except:
            self.fields['nominalMagnification'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Nominal magnification", required=False)
            self.fields['nominalMagnification'].widget.attrs['disabled'] = True 
            self.fields['nominalMagnification'].widget.attrs['class'] = 'disabled'
        
        # Calibrated Magnification
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().calibratedMagnification is not None:
                self.fields['calibratedMagnification'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'calibratedMagnification\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().calibratedMagnification, label="Calibrated magnification", required=False)
            else:
                self.fields['calibratedMagnification'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'calibratedMagnification\', this.value);'}), label="Calibrated magnification", required=False)
            self.fields['calibratedMagnification'].widget.attrs['disabled'] = True 
            self.fields['calibratedMagnification'].widget.attrs['class'] = 'disable'
        except:
            self.fields['calibratedMagnification'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Calibrated magnification", required=False)
            self.fields['calibratedMagnification'].widget.attrs['disabled'] = True 
            self.fields['calibratedMagnification'].widget.attrs['class'] = 'disabled'
        
        # Lens NA
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().lensNA is not None:
                self.fields['lensNA'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'lensNA\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().lensNA, label="Lens NA", required=False)
            else:
                self.fields['lensNA'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'lensNA\', this.value);'}), required=False)
            self.fields['lensNA'].widget.attrs['disabled'] = True 
            self.fields['lensNA'].widget.attrs['class'] = 'disable'
        except:
            self.fields['lensNA'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Lens NA", required=False)
            self.fields['lensNA'].widget.attrs['disabled'] = True 
            self.fields['lensNA'].widget.attrs['class'] = 'disabled'
        
        # Immersion
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().immersion is not None:
                self.fields['immersion'] = MetadataModelChoiceField(queryset=kwargs['initial']['immersions'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'immersion\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().immersion, required=False) 
            else:
                self.fields['immersion'] = MetadataModelChoiceField(queryset=kwargs['initial']['immersions'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['image'].id)+', \'immersion\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['immersion'].widget.attrs['disabled'] = True 
            self.fields['immersion'].widget.attrs['class'] = 'disable'
        except:
            self.fields['immersion'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['immersion'].widget.attrs['disabled'] = True 
            self.fields['immersion'].widget.attrs['class'] = 'disabled'
        
        # Correction
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().correction is not None:
                self.fields['correction'] = MetadataModelChoiceField(queryset=kwargs['initial']['corrections'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'correction\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().correction, required=False) 
            else:
                self.fields['correction'] = MetadataModelChoiceField(queryset=kwargs['initial']['corrections'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'correction\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['correction'].widget.attrs['disabled'] = True 
            self.fields['correction'].widget.attrs['class'] = 'disable'
        except:
            self.fields['correction'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['correction'].widget.attrs['disabled'] = True 
            self.fields['correction'].widget.attrs['class'] = 'disabled'
        
        # Working Distance
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().workingDistance is not None:
                self.fields['workingDistance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'workingDistance\', this.value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().workingDistance, label="Working distance", required=False)
            else:
                self.fields['workingDistance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'workingDistance\', this.value);'}), label="Working distance", required=False)
            self.fields['workingDistance'].widget.attrs['disabled'] = True 
            self.fields['workingDistance'].widget.attrs['class'] = 'disable'
        except:
            self.fields['workingDistance'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Working distance", required=False)
            self.fields['workingDistance'].widget.attrs['disabled'] = True 
            self.fields['workingDistance'].widget.attrs['class'] = 'disabled'
        
        # Iris
        try:
            if kwargs['initial']['objectiveSettings'].getObjective().iris is not None:
                self.fields['iris'] = forms.ChoiceField(choices=self.BOOLEAN_CHOICES,  widget=forms.Select(attrs={'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'iris\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['objectiveSettings'].getObjective().iris, required=False)
            else:
                self.fields['iris'] = forms.ChoiceField(choices=self.BOOLEAN_CHOICES,  widget=forms.Select(attrs={'onchange':'javascript:saveMetadata('+str(kwargs['initial']['objectiveSettings'].id)+', \'iris\', this.options[this.selectedIndex].value);'}), required=False)
            self.fields['iris'].widget.attrs['disabled'] = True 
            self.fields['iris'].widget.attrs['class'] = 'disable'
        except:
            self.fields['iris'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['iris'].widget.attrs['disabled'] = True 
            self.fields['iris'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['model', 'manufacturer', 'serialNumber', 'nominalMagnification', 'calibratedMagnification', 'lensNA', 'immersion', 'correction', 'workingDistance', 'iris', 'correctionCollar',  'medium', 'refractiveIndex'] 
    

class MetadataFilterForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataFilterForm, self).__init__(*args, **kwargs)
        
        # Filter 
        
        # Manufacturer
        try:
            if kwargs['initial']['filter'].manufacturer is not None:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'manufacturer\', this.value);'}), initial=kwargs['initial']['filter'].manufacturer, required=False)
            else:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'manufacturer\', this.value);'}), required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disable'
        except:
            self.fields['manufacturer'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disabled'
        
        # Model
        try:
            if kwargs['initial']['filter'].model is not None:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['filter'].model, required=False)
            else:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'model\', this.value);'}), required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disable'
        except:
            self.fields['model'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disabled'
        
        # Lot number
        try:
            if kwargs['initial']['filter'].lotNumber is not None:
                self.fields['lotNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'lotNumber\', this.value);'}), initial=kwargs['initial']['filter'].lotNumber, label="Lot number", required=False)
            else:
                self.fields['lotNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'lotNumber\', this.value);'}), label="Lot number", required=False)
            self.fields['lotNumber'].widget.attrs['disabled'] = True 
            self.fields['lotNumber'].widget.attrs['class'] = 'disable'
        except:
            self.fields['lotNumber'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Lot number", required=False)
            self.fields['lotNumber'].widget.attrs['disabled'] = True 
            self.fields['lotNumber'].widget.attrs['class'] = 'disabled'
        
        # Filter wheel
        try:
            if kwargs['initial']['filter'].filterWheel is not None:
                self.fields['filterWheel'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'filterWheel\', this.value);'}), initial=kwargs['initial']['filter'].filterWheel, label="Filter wheel", required=False)
            else:
                self.fields['filterWheel'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'filterWheel\', this.value);'}), label="Filter wheel", required=False)
            self.fields['filterWheel'].widget.attrs['disabled'] = True 
            self.fields['filterWheel'].widget.attrs['class'] = 'disable'
        except:
            self.fields['filterWheel'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Filter wheel", required=False)
            self.fields['filterWheel'].widget.attrs['disabled'] = True 
            self.fields['filterWheel'].widget.attrs['class'] = 'disabled'
        
        # Type
        try:
            if kwargs['initial']['filter'].type is not None:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['types'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['filter'].id)+', \'type\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['filter'].getFilterType().value, required=False) 
            else:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['types'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['filter'].id)+', \'type\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disable'
        except:
            self.fields['type'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disabled'
        
        # Cut in
        try:
            if kwargs['initial']['filter'].transmittanceRange is not None:
                self.fields['cutIn'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutIn\', this.value);'}), initial=kwargs['initial']['filter'].getTransmittanceRange().cutIn, label="Cut in", required=False)
            else:
                self.fields['cutIn'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutIn\', this.value);'}), label="Cut in", required=False)
            self.fields['cutIn'].widget.attrs['disabled'] = True 
            self.fields['cutIn'].widget.attrs['class'] = 'disable'
        except:
            self.fields['cutIn'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Cut in", required=False)
            self.fields['cutIn'].widget.attrs['disabled'] = True 
            self.fields['cutIn'].widget.attrs['class'] = 'disabled'
        
        # Cut out
        try:
            if kwargs['initial']['filter'].transmittanceRange is not None:
                self.fields['cutOut'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutOut\', this.value);'}), initial=kwargs['initial']['filter'].getTransmittanceRange().cutOut, label="Cut out", required=False)
            else:
                self.fields['cutOut'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutOut\', this.value);'}), label="Cut out", required=False)
            self.fields['cutOut'].widget.attrs['disabled'] = True 
            self.fields['cutOut'].widget.attrs['class'] = 'disable'
        except:
            self.fields['cutOut'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Cut out", required=False)
            self.fields['cutOut'].widget.attrs['disabled'] = True 
            self.fields['cutOut'].widget.attrs['class'] = 'disabled'
        
        # Cut in tolerance
        try:
            if kwargs['initial']['filter'].transmittanceRange is not None:
                self.fields['cutInTolerance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutInTolerance\', this.value);'}), initial=kwargs['initial']['filter'].getTransmittanceRange().cutInTolerance, label="Cut in tolerance", required=False)
            else:
                self.fields['cutInTolerance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutInTolerance\', this.value);'}), label="Cut in tolerance", required=False)
            self.fields['cutInTolerance'].widget.attrs['disabled'] = True 
            self.fields['cutInTolerance'].widget.attrs['class'] = 'disable'
        except:
            self.fields['cutInTolerance'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Cut in tolerance", required=False)
            self.fields['cutInTolerance'].widget.attrs['disabled'] = True 
            self.fields['cutInTolerance'].widget.attrs['class'] = 'disabled'
        
        # Cut on tolerance
        try:
            if kwargs['initial']['filter'].transmittanceRange is not None:
                self.fields['cutOutTolerance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutOut\', this.value);'}), initial=kwargs['initial']['filter'].getTransmittanceRange().cutOutTolerance, label="Cut out tolerance", required=False)
            else:
                self.fields['cutOutTolerance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'cutOut\', this.value);'}), label="Cut out tolerance", required=False)
            self.fields['cutOutTolerance'].widget.attrs['disabled'] = True 
            self.fields['cutOutTolerance'].widget.attrs['class'] = 'disable'
        except:
            self.fields['cutOutTolerance'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Cut out tolerance", required=False)
            self.fields['cutOutTolerance'].widget.attrs['disabled'] = True 
            self.fields['cutOutTolerance'].widget.attrs['class'] = 'disabled'
        
        # Transmittance
        try:
            if kwargs['initial']['filter'].transmittanceRange is not None:
                self.fields['transmittance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'transmittance\', this.value);'}), initial=kwargs['initial']['filter'].getTransmittanceRange().transmittance, required=False)
            else:
                self.fields['transmittance'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['filter'].id)+', \'transmittance\', this.value);'}), required=False)
            self.fields['transmittance'].widget.attrs['disabled'] = True 
            self.fields['transmittance'].widget.attrs['class'] = 'disable'
        except:
            self.fields['transmittance'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['transmittance'].widget.attrs['disabled'] = True 
            self.fields['transmittance'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['manufacturer', 'model', 'lotNumber', 'type', 'filterWheel', 'cutIn', 'cutOut', 'cutInTolerance', 'cutOutTolerance', 'transmittance']


class MetadataDetectorForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataDetectorForm, self).__init__(*args, **kwargs)
        
        # Filter 
        
        # Manufacturer
        try:
            if kwargs['initial']['detector'] is not None:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'manufacturer\', this.value);'}), initial=kwargs['initial']['detector'].manufacturer, required=False)
            else:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'manufacturer\', this.value);'}), required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disable'
        except:
            self.fields['manufacturer'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disabled'
        
        # Model
        try:
            if kwargs['initial']['detector'] is not None:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['detector'].model, required=False)
            else:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'model\', this.value);'}), required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disable'
        except:
            self.fields['model'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disabled'
        
        # Type
        try:
            if kwargs['initial']['detector'] is not None:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['types'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['detector'].id)+', \'type\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['detector'].type, required=False) 
            else:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['types'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['detector'].id)+', \'type\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disable'
        except:
            self.fields['type'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disabled'
        
        # Gain
        try:
            if kwargs['initial']['detectorSettings'] is not None:
                self.fields['gain'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detectorSettings'].id)+', \'gain\', this.value);'}), initial=kwargs['initial']['detectorSettings'].gain, required=False)
            elif kwargs['initial']['detector'] is not None:
                self.fields['gain'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'gain\', this.value);'}), initial=kwargs['initial']['detector'].gain, required=False)
            else:
                self.fields['gain'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detectorSettings'].id)+', \'gain\', this.value);'}), required=False)
            self.fields['gain'].widget.attrs['disabled'] = True 
            self.fields['gain'].widget.attrs['class'] = 'disable'
        except:
            self.fields['gain'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['gain'].widget.attrs['disabled'] = True 
            self.fields['gain'].widget.attrs['class'] = 'disabled'
        
        # Voltage
        try:
            if kwargs['initial']['detectorSettings'] is not None:
                self.fields['voltage'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detectorSettings'].id)+', \'voltage\', this.value);'}), initial=kwargs['initial']['detectorSettings'].voltage, required=False)
            elif kwargs['initial']['detector'] is not None:
                self.fields['voltage'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'voltage\', this.value);'}), initial=kwargs['initial']['detector'].voltage, required=False)
            else:
                self.fields['voltage'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detectorSettings'].id)+', \'voltage\', this.value);'}), required=False)
            self.fields['voltage'].widget.attrs['disabled'] = True 
            self.fields['voltage'].widget.attrs['class'] = 'disable'
        except:
            self.fields['voltage'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['voltage'].widget.attrs['disabled'] = True 
            self.fields['voltage'].widget.attrs['class'] = 'disabled'
        
        # Offset
        try:
            if kwargs['initial']['detectorSettings'] is not None:
                self.fields['offsetValue'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detectorSettings'].id)+', \'offsetValue\', this.value);'}), initial=kwargs['initial']['detectorSettings'].offsetValue, label="Offset", required=False)
            elif kwargs['initial']['detector'] is not None:
                self.fields['offsetValue'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'offsetValue\', this.value);'}), initial=kwargs['initial']['detector'].offsetValue, label="Offset", required=False)
            else:
                self.fields['offsetValue'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detectorSettings'].id)+', \'offsetValue\', this.value);'}), label="Offset", required=False)
            self.fields['offsetValue'].widget.attrs['disabled'] = True 
            self.fields['offsetValue'].widget.attrs['class'] = 'disable'
        except:
            self.fields['offsetValue'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Offset", required=False)
            self.fields['offsetValue'].widget.attrs['disabled'] = True 
            self.fields['offsetValue'].widget.attrs['class'] = 'disabled'
        
        # Zoom
        try:
            if kwargs['initial']['detector'] is not None:
                self.fields['zoom'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'zoom\', this.value);'}), initial=kwargs['initial']['detector'].zoom, required=False)
            else:
                self.fields['zoom'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'voltage\', this.value);'}), required=False)
            self.fields['zoom'].widget.attrs['disabled'] = True 
            self.fields['zoom'].widget.attrs['class'] = 'disable'
        except:
            self.fields['zoom'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['zoom'].widget.attrs['disabled'] = True 
            self.fields['zoom'].widget.attrs['class'] = 'disabled'
        
        # Amplification gain
        try:
            if kwargs['initial']['detector'] is not None:
                self.fields['amplificationGain'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'amplificationGain\', this.value);'}), initial=kwargs['initial']['detector'].amplificationGain, label="Amplification gain", required=False)
            else:
                self.fields['amplificationGain'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['detector'].id)+', \'amplificationGain\', this.value);'}), label="Amplification gain", required=False)
            self.fields['amplificationGain'].widget.attrs['disabled'] = True 
            self.fields['amplificationGain'].widget.attrs['class'] = 'disable'
        except:
            self.fields['amplificationGain'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Amplification gain", required=False)
            self.fields['amplificationGain'].widget.attrs['disabled'] = True 
            self.fields['amplificationGain'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['manufacturer', 'model', 'type', 'gain', 'voltage', 'offsetValue', 'zoom', 'amplificationGain']


class MetadataLightSourceForm(forms.Form):
    
    BOOLEAN_CHOICES = (
        ('', '---------'),
        ('True', 'True'),
        ('False', 'False'),
    )
        
    def __init__(self, *args, **kwargs):
        super(MetadataLightSourceForm, self).__init__(*args, **kwargs)
        
        # Filter 
        
        # Manufacturer
        try:
            if kwargs['initial']['lightSource'].getLightSource().manufacturer is not None:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['lightSource'].getLightSource().manufacturer, required=False)
            else:
                self.fields['manufacturer'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'model\', this.value);'}), required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disable'
        except:
            self.fields['manufacturer'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['manufacturer'].widget.attrs['disabled'] = True 
            self.fields['manufacturer'].widget.attrs['class'] = 'disabled'
        
        # Model
        try:
            if kwargs['initial']['lightSource'].getLightSource().model is not None:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'model\', this.value);'}), initial=kwargs['initial']['lightSource'].getLightSource().model, required=False)
            else:
                self.fields['model'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'model\', this.value);'}), required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disable'
        except:
            self.fields['model'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['model'].widget.attrs['disabled'] = True 
            self.fields['model'].widget.attrs['class'] = 'disabled'
        
        # Serial Number
        try:
            if kwargs['initial']['lightSource'].getLightSource().serialNumber is not None:
                self.fields['serialNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'serialNumber\', this.value);'}), initial=kwargs['initial']['lightSource'].getLightSource().serialNumber, label="Serial number", required=False)
            else:
                self.fields['serialNumber'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'serialNumber\', this.value);'}), label="Serial number", required=False)
            self.fields['serialNumber'].widget.attrs['disabled'] = True 
            self.fields['serialNumber'].widget.attrs['class'] = 'disable'
        except:
            self.fields['serialNumber'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Serial number", required=False)
            self.fields['serialNumber'].widget.attrs['disabled'] = True 
            self.fields['serialNumber'].widget.attrs['class'] = 'disabled'
        
        # Power
        try:
            if kwargs['initial']['lightSource'].getLightSource().power is not None:
                self.fields['power'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'power\', this.value);'}), initial=kwargs['initial']['lightSource'].getLightSource().power, required=False)
            else:
                self.fields['power'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'power\', this.value);'}), required=False)
            self.fields['power'].widget.attrs['disabled'] = True 
            self.fields['power'].widget.attrs['class'] = 'disable'
        except:
            self.fields['power'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['power'].widget.attrs['disabled'] = True 
            self.fields['power'].widget.attrs['class'] = 'disabled'
        
        # Type
        try:
            if kwargs['initial']['lightSource'].getLightSource().type is not None:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['types'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'type\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['lightSource'].getLightSource().type, required=False) 
            else:
                self.fields['type'] = MetadataModelChoiceField(queryset=kwargs['initial']['types'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'type\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disable'
        except:
            self.fields['type'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['type'].widget.attrs['disabled'] = True 
            self.fields['type'].widget.attrs['class'] = 'disabled'
        
        # Medium
        try:
            if kwargs['initial']['lightSource'].getLightSource().laserMedium is not None:
                self.fields['medium'] = MetadataModelChoiceField(queryset=kwargs['initial']['mediums'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'medium\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['lightSource'].getLightSource().laserMedium, required=False) 
            else:
                self.fields['medium'] = MetadataModelChoiceField(queryset=kwargs['initial']['mediums'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'medium\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['medium'].widget.attrs['disabled'] = True 
            self.fields['medium'].widget.attrs['class'] = 'disable'
        except:
            self.fields['medium'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['medium'].widget.attrs['disabled'] = True 
            self.fields['medium'].widget.attrs['class'] = 'disabled'
        
        # Wavelength
        try:
            if kwargs['initial']['lightSource'].wavelength is not None:
                self.fields['wavelength'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'wavelength\', this.value);'}), initial=kwargs['initial']['lightSource'].wavelength, required=False)
            else:
                self.fields['wavelength'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'wavelength\', this.value);'}), required=False)
            self.fields['wavelength'].widget.attrs['disabled'] = True 
            self.fields['wavelength'].widget.attrs['class'] = 'disable'
        except:
            self.fields['wavelength'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['wavelength'].widget.attrs['disabled'] = True 
            self.fields['wavelength'].widget.attrs['class'] = 'disabled'
        
        # FrequencyMultiplication
        try:
            if kwargs['initial']['lightSource'].getLightSource().frequencyMultiplication is not None:
                self.fields['frequencyMultiplication'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'frequencyMultiplication\', this.value);'}), initial=kwargs['initial']['lightSource'].getLightSource().frequencyMultiplication, label="Frequency Multiplication", required=False)
            else:
                self.fields['frequencyMultiplication'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'frequencyMultiplication\', this.value);'}), label="Frequency Multiplication", required=False)
            self.fields['frequencyMultiplication'].widget.attrs['disabled'] = True 
            self.fields['frequencyMultiplication'].widget.attrs['class'] = 'disable'
        except:
            self.fields['frequencyMultiplication'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Frequency Multiplication", required=False)
            self.fields['frequencyMultiplication'].widget.attrs['disabled'] = True 
            self.fields['frequencyMultiplication'].widget.attrs['class'] = 'disabled'
        
        # Tuneable
        try:
            if kwargs['initial']['lightSource'].getLightSource().tuneable is not None:
                self.fields['tuneable'] = forms.ChoiceField(choices=self.BOOLEAN_CHOICES,  widget=forms.Select(attrs={'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'tuneable\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['lightSource'].getLightSource().tuneable, required=False)
            else:
                self.fields['tuneable'] = forms.ChoiceField(choices=self.BOOLEAN_CHOICES,  widget=forms.Select(attrs={'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'tuneable\', this.options[this.selectedIndex].value);'}), required=False)
            self.fields['tuneable'].widget.attrs['disabled'] = True 
            self.fields['tuneable'].widget.attrs['class'] = 'disable'
        except:
            self.fields['tuneable'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['tuneable'].widget.attrs['disabled'] = True 
            self.fields['tuneable'].widget.attrs['class'] = 'disabled'            
        
        # Pulse
        try:
            if kwargs['initial']['lightSource'].getLightSource().pulse is not None:
                self.fields['pulse'] = MetadataModelChoiceField(queryset=kwargs['initial']['pulses'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'pulse\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['lightSource'].getLightSource().pulse, required=False) 
            else:
                self.fields['pulse'] = MetadataModelChoiceField(queryset=kwargs['initial']['pulses'], empty_label=u"---------", widget=forms.Select(attrs={'onchange':'saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'pulse\', this.options[this.selectedIndex].value);'}), required=False) 
            self.fields['pulse'].widget.attrs['disabled'] = True 
            self.fields['pulse'].widget.attrs['class'] = 'disable'
        except:
            self.fields['pulse'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['pulse'].widget.attrs['disabled'] = True 
            self.fields['pulse'].widget.attrs['class'] = 'disabled'
        
        # Repetition Rate
        try:
            if kwargs['initial']['lightSource'].getLightSource().repetitionRate is not None:
                self.fields['repetitionRate'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'repetitionRate\', this.value);'}), initial=kwargs['initial']['lightSource'].getLightSource().repetitionRate, label="Repetition rate", required=False)
            else:
                self.fields['repetitionRate'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'repetitionRate\', this.value);'}), label="Repetition rate", required=False)
            self.fields['repetitionRate'].widget.attrs['disabled'] = True 
            self.fields['repetitionRate'].widget.attrs['class'] = 'disable'
        except:
            self.fields['repetitionRate'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Repetition rate", required=False)
            self.fields['repetitionRate'].widget.attrs['disabled'] = True 
            self.fields['repetitionRate'].widget.attrs['class'] = 'disabled'
        
        # Pockel Cell
        try:
            if kwargs['initial']['lightSource'].getLightSource().pockelCell is not None:
                self.fields['pockelCell'] = forms.ChoiceField(choices=self.BOOLEAN_CHOICES,  widget=forms.Select(attrs={'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'pockelCell\', this.options[this.selectedIndex].value);'}), initial=kwargs['initial']['lightSource'].getLightSource().pockelCell, label="Pockel Cell", required=False)
            else:
                self.fields['pockelCell'] = forms.ChoiceField(choices=self.BOOLEAN_CHOICES,  widget=forms.Select(attrs={'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'pockelCell\', this.options[this.selectedIndex].value);'}), label="Pockel Cell", required=False)
            self.fields['pockelCell'].widget.attrs['disabled'] = True 
            self.fields['pockelCell'].widget.attrs['class'] = 'disable'
        except:
            self.fields['pockelCell'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Pockel Cell", required=False)
            self.fields['pockelCell'].widget.attrs['disabled'] = True 
            self.fields['pockelCell'].widget.attrs['class'] = 'disabled'
        
        # Attenuation
        try:
            if kwargs['initial']['lightSource'].attenuation is not None:
                self.fields['attenuation'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'attenuation\', this.value);'}), initial=kwargs['initial']['lightSource'].attenuation, required=False)
            else:
                self.fields['attenuation'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['lightSource'].id)+', \'attenuation\', this.value);'}), required=False)
            self.fields['attenuation'].widget.attrs['disabled'] = True 
            self.fields['attenuation'].widget.attrs['class'] = 'disable'
        except:
            self.fields['attenuation'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['attenuation'].widget.attrs['disabled'] = True 
            self.fields['attenuation'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['manufacturer', 'model', 'serialNumber', 'power', 'type', 'medium', 'wavelength', 'frequencyMultiplication', 'tuneable', 'pulse' , 'repetitionRate', 'pockelCell']
    

class MetadataEnvironmentForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataEnvironmentForm, self).__init__(*args, **kwargs)
        
        # Imaging environment 
        
        # Temperature
        try:
            if kwargs['initial']['image'].getImagingEnvironment().temperature is not None:
                self.fields['temperature'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'temperature\', this.value);'}), initial=kwargs['initial']['image'].getImagingEnvironment().temperature, required=False)
            else:
                self.fields['temperature'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'temperature\', this.value);'}), required=False)
            self.fields['temperature'].widget.attrs['disabled'] = True 
            self.fields['temperature'].widget.attrs['class'] = 'disable'
        except:
            self.fields['temperature'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['temperature'].widget.attrs['disabled'] = True 
            self.fields['temperature'].widget.attrs['class'] = 'disabled'
        
        # Air Pressure
        try:
            if kwargs['initial']['image'].getImagingEnvironment().airPressure is not None:
                self.fields['airPressure'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'airPressure\', this.value);'}), initial=kwargs['initial']['image'].getImagingEnvironment().airPressure, label="Air Pressure", required=False)
            else:
                self.fields['airPressure'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'airPressure\', this.value);'}), label="Air Pressure", required=False)
            self.fields['airPressure'].widget.attrs['disabled'] = True 
            self.fields['airPressure'].widget.attrs['class'] = 'disable'
        except:
            self.fields['airPressure'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), label="Air Pressure", initial="N/A", required=False)
            self.fields['airPressure'].widget.attrs['disabled'] = True 
            self.fields['airPressure'].widget.attrs['class'] = 'disabled'
        
        # Humidity
        try:
            if kwargs['initial']['image'].getImagingEnvironment().humidity is not None:
                self.fields['humidity'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'humidity\', this.value);'}), initial=kwargs['initial']['image'].getImagingEnvironment().humidity, required=False)
            else:
                self.fields['humidity'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'humidity\', this.value);'}), required=False)
            self.fields['humidity'].widget.attrs['disabled'] = True 
            self.fields['humidity'].widget.attrs['class'] = 'disable'
        except:
            self.fields['humidity'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", required=False)
            self.fields['humidity'].widget.attrs['disabled'] = True 
            self.fields['humidity'].widget.attrs['class'] = 'disabled'
        
        # CO2 percent
        try:
            if kwargs['initial']['image'].getImagingEnvironment().co2percent is not None:
                self.fields['co2percent'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'co2percent\', this.value);'}), initial=kwargs['initial']['image'].getImagingEnvironment().co2percent, label="CO2 [%]", required=False)
            else:
                self.fields['co2percent'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'co2percent\', this.value);'}), label="CO2 [%]", required=False)
            self.fields['co2percent'].widget.attrs['disabled'] = True 
            self.fields['co2percent'].widget.attrs['class'] = 'disable'
        except:
            self.fields['co2percent'] = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="CO2 [%]", required=False)
            self.fields['co2percent'].widget.attrs['disabled'] = True 
            self.fields['co2percent'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['airPressure', 'co2percent', 'humidity', 'temperature']

class MetadataStageLabelForm(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(MetadataStageLabelForm, self).__init__(*args, **kwargs)
        
        # Stage label
        
        # Position x
        try:
            if kwargs['initial']['image'].getStageLabel() is not None:
                self.fields['positionx'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'positionx\', this.value);'}), initial=kwargs['initial']['image'].getStageLabel().positionx, label="Position X", required=False)
            else:
                self.fields['positionx'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'positionx\', this.value);'}), label="Position X", required=False)
            self.fields['positionx'].widget.attrs['disabled'] = True 
            self.fields['positionx'].widget.attrs['class'] = 'disable'
        except:
            self.fields['positionx'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Position X", required=False)
            self.fields['positionx'].widget.attrs['disabled'] = True 
            self.fields['positionx'].widget.attrs['class'] = 'disabled'
        
        # Position y
        try:
            if kwargs['initial']['image'].getStageLabel() is not None:
                self.fields['positiony'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'positiony\', this.value);'}), initial=kwargs['initial']['image'].getStageLabel().positiony, label="Position Y", required=False)
            else:
                self.fields['positiony'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'positiony\', this.value);'}), label="Position Y", required=False)
            self.fields['positiony'].widget.attrs['disabled'] = True 
            self.fields['positiony'].widget.attrs['class'] = 'disable'
        except:
            self.fields['positiony'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Position Y", required=False)
            self.fields['positiony'].widget.attrs['disabled'] = True 
            self.fields['positiony'].widget.attrs['class'] = 'disabled'
        
        # Position z
        try:
            if kwargs['initial']['image'].getStageLabel() is not None:
                self.fields['positionz'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'positionz\', this.value);'}), initial=kwargs['initial']['image'].getStageLabel().positionz, label="Position Z", required=False)
            else:
                self.fields['positionz'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25, 'onchange':'javascript:saveMetadata('+str(kwargs['initial']['image'].id)+', \'positionz\', this.value);'}), label="Position Z", required=False)
            self.fields['positionz'].widget.attrs['disabled'] = True 
            self.fields['positionz'].widget.attrs['class'] = 'disable'
        except:
            self.fields['positionz'] = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'size':25}), initial="N/A", label="Position Z", required=False)
            self.fields['positionz'].widget.attrs['disabled'] = True 
            self.fields['positionz'].widget.attrs['class'] = 'disabled'
        
        self.fields.keyOrder = ['positionx', 'positiony', 'positionz']