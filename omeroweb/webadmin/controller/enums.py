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

import omero

import omero.rtypes
from omero.rtypes import *

from omero_model_AcquisitionModeI import AcquisitionModeI
from omero_model_ArcTypeI import ArcTypeI
from omero_model_BinningI import BinningI
from omero_model_ContrastMethodI import ContrastMethodI
from omero_model_ContrastMethodI import ContrastMethodI
from omero_model_CorrectionI import CorrectionI
from omero_model_DetectorTypeI import DetectorTypeI
from omero_model_DimensionOrderI import DimensionOrderI
from omero_model_EventTypeI import EventTypeI
from omero_model_ExperimentTypeI import ExperimentTypeI
from omero_model_FamilyI import FamilyI
from omero_model_FilamentTypeI import FilamentTypeI
from omero_model_FilterTypeI import FilterTypeI
from omero_model_FormatI import FormatI
from omero_model_IlluminationI import IlluminationI
from omero_model_ImmersionI import ImmersionI
from omero_model_JobStatusI import JobStatusI
from omero_model_LaserMediumI import LaserMediumI
from omero_model_LaserTypeI import LaserTypeI
from omero_model_MediumI import MediumI
from omero_model_MicrobeamManipulationTypeI import MicrobeamManipulationTypeI
from omero_model_MicroscopeTypeI import MicroscopeTypeI
from omero_model_PhotometricInterpretationI import PhotometricInterpretationI
from omero_model_PixelsTypeI import PixelsTypeI
from omero_model_PulseI import PulseI
from omero_model_RenderingModelI import RenderingModelI

from webadmin.controller import BaseController

class BaseEnums(BaseController):

    klass = None
    enums = None
    enumsCount = 0
    entries = None
    entriesCount = 0
    
    def __init__(self, conn, klass=None):
        BaseController.__init__(self, conn)
        if klass is not None and klass!="":
            self.klass = klass
            self.entries = list(self.conn.getEnumerationEntries(self.klass))
        else:
            self.enums = self.conn.getEnumerationsWithEntries()
            self.enumsCount = len(self.enums)     
               
            ext = self.enums
            org = self.conn.getOriginalEnumerations()
            
            result = set()
            if len(ext.keys()) == len(org.keys()):
                result.update(org.keys())
            else:                
                result.update(ext.keys())
                result.update(org.keys())
            
            check = dict()
            for key in list(result):
                o_enums = org.get(key)
                e_enums = ext.get(key)
                if o_enums is not None and e_enums is not None:  
                    if len(o_enums) == len(e_enums):            
                        for e in e_enums:
                            flag = False
                            for o in o_enums:
                                if o.value == e.value:
                                    flag = True
                                    break
                            check[key] = flag
                            if not flag:
                                break
                    else:
                        check[key] = False
            self.check = check

    def saveEntry(self, entry):
        obj = None
        try:
            obj = self.conn.getEnumeration(self.klass, entry)._obj
        except:
            pass
        if obj is None:
            obj = eval("%s" % (self.klass))()
            obj.setValue(rstring(str(entry))) 
            self.conn.createEnumeration(obj)
    
    def saveEntries(self, entries):
        new_entries = list()
        for e in self.entries:
            new_entry = rstring(str(entries[unicode(e.id)]))
            new_entries.append(e._obj.setValue(new_entry))
        self.conn.updateEnumerations(new_entries)
    
    def deleteEntry(self, eid):
        try:
            obj = self.conn.getEnumerationById(self.klass, eid)._obj
            if obj is not None:
                self.conn.deleteEnumeration(obj)
        except Exception, x:
            raise AttributeError(x)

    def resetEnumerations(self):
        self.conn.resetEnumerations(self.klass)