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

import operator

from omero_model_PermissionsI import PermissionsI

class BaseController(object):
    
    conn = None
    
    def __init__(self, conn, **kw):
        self.conn = conn
    
    def sortByAttr(self, seq, attr, reverse=False):
        # Use the "Schwartzian transform".
        # Wrapped object only.
        #intermed = map(None, map(getattr, seq, (attr,)*len(seq)), xrange(len(seq)), seq)
        #intermed.sort()
        #if reverse:
        #    intermed.reverse()
        #return map(operator.getitem, intermed, (-1,) * len(intermed))
        
        intermed = list()
        for i in xrange(len(seq)):
            val = self.getAttribute(seq[i],attr)
            intermed.append((val, i, seq[i]))
        
        intermed.sort()
        if reverse:
            intermed.reverse()
        return [ tup[-1] for tup in intermed ]
    
    
    def getAttribute(self, o,a):
        attr = a.split(".")
        if len(attr) > 1:
            for i in xrange(len(attr)):
                if hasattr(o,attr[i]):
                    rv = getattr(o,attr[i])
                    if hasattr(rv,'val'):
                        return getattr(rv,'val')
                    else:
                        attr.remove(attr[i])
                        return self.getAttribute(rv, ".".join(attr))
        else:
            if hasattr(o,attr[0]):
                rv = getattr(o,attr[0])
                if hasattr(rv,'val'):
                    return getattr(rv,'val')
                else:
                    return rv
    
    #####################################################################
    # Permissions
    
    def setObjectPermissions(self, obj, permissions):
        if obj.details.getPermissions() is None:
            perm = PermissionsI()
        else:
            perm = obj.details.getPermissions()
            
        if permissions['owner'] == 'rw':
            perm.setUserRead(True)
            perm.setUserWrite(True)
        elif permissions['owner'] == 'w':
            perm.setUserRead(False)
            perm.setUserWrite(True)
        elif permissions['owner'] == 'r':
            perm.setUserRead(True)
            perm.setUserWrite(False)
        else:
            perm.setUserRead(False)
            perm.setUserWrite(False)
        
        if permissions['group'] == 'rw':
            perm.setGroupRead(True)
            perm.setGroupWrite(True)
        elif permissions['group'] == 'w':
            perm.setGroupRead(False)
            perm.setGroupWrite(True)
        elif permissions['group'] == 'r':
            perm.setGroupRead(True)
            perm.setGroupWrite(False)
        else:
            perm.setGroupRead(False)
            perm.setGroupWrite(False)
        
        if permissions['world'] == 'rw':
            perm.setWorldRead(True)
            perm.setWorldWrite(True)
        elif permissions['world'] == 'w':
            perm.setWorldRead(False)
            perm.setWorldWrite(True)
        elif permissions['world'] == 'r':
            perm.setWorldRead(True)
            perm.setWorldWrite(False)
        else:
            perm.setWorldRead(False)
            perm.setWorldWrite(False)
    
        obj.details.setPermissions(perm)
        
    def getObjectPermissions(self, obj):
        perm = None
        if obj.details.getPermissions() is None:
            raise AttributeError('Object has no permissions')
        else:
            perm = obj.details.getPermissions()
        
        permissions = {'owner':None, 'group':None, 'world':None}
        if perm.isUserRead() and perm.isUserWrite():
            permissions['owner'] = 'rw'
        elif not perm.isUserRead() and perm.isUserWrite():
            permissions['owner'] = 'w'
        elif perm.isUserRead() and not perm.isUserWrite():
            permissions['owner'] = 'r'
        else:
            permissions['owner'] = None
        
        if perm.isGroupRead() and perm.isGroupWrite():
            permissions['group'] = 'rw'
        elif not perm.isGroupRead() and perm.isGroupWrite():
            permissions['group'] = 'w'
        elif perm.isGroupRead() and not perm.isGroupWrite():
            permissions['group'] = 'r'
        else:
            permissions['group'] = None
        
        if perm.isWorldRead() and perm.isWorldWrite():
            permissions['world'] = 'rw'
        elif not perm.isWorldRead() and perm.isWorldWrite():
            permissions['world'] = 'w'
        elif perm.isWorldRead() and not perm.isWorldWrite():
            permissions['world'] = 'r'
        else:
            permissions['world'] = None
        
        return permissions