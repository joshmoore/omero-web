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

import string
import datetime
import time

import omero
from omero.rtypes import *
from omero_model_ImageI import ImageI
from omero_model_DatasetI import DatasetI
from omero_model_ProjectI import ProjectI

from webclient.controller import BaseController

class BaseShare(BaseController):

    shares = None
    shSize = None
    ownShares = None
    oshSize = None
    memberShares = None
    mshSize = None
    
    share = None
    imageInShare = None
    datasetInShare = None
    projectInShare = None
    imgSize = 0
    dsSize = 0
    prSize = 0
    membersInShare = None

    comments = None
    cmSize = None

    def __init__(self, menu, conn, conn_share=None, share_id=None, action=None, **kw):
        BaseController.__init__(self, conn)
        self.conn_share = conn_share
        if share_id: 
            self.share = self.conn.getShare(share_id)
            self.eContext['breadcrumb'] = [ menu.title(), "Share", action ]
        elif action:
            self.eContext['breadcrumb'] = ["Basket", action ]
        else:
            self.eContext['breadcrumb'] = [ menu.title() ]

    def createShare(self, host, blitz_id, imageInBasket, datasetInBasket, projectInBasket, message, expiretion, members, enable):
        # only for python 2.5
        # d1 = datetime.strptime(expiretion+" 23:59:59", "%Y-%m-%d %H:%M:%S")
        d1 = datetime.datetime(*(time.strptime((expiretion+" 23:59:59"), "%Y-%m-%d %H:%M:%S")[0:6]))
        expiretion_date = rtime(long(time.mktime(d1.timetuple())+1e-6*d1.microsecond)*1000)
        ms = [str(m) for m in members]
        #gs = str(guests).split(';')
        if enable is not None:
            enable = True
        else:
            enable = False
        self.conn.createShare(host, int(blitz_id), imageInBasket, datasetInBasket, projectInBasket, message, expiretion_date, ms, enable)

    def updateShare(self, message, expiretion, members, enable):
        # only for python 2.5
        # d1 = datetime.strptime(expiretion+" 23:59:59", "%Y-%m-%d %H:%M:%S")
        d1 = datetime.datetime(*(time.strptime((expiretion+" 23:59:59"), "%Y-%m-%d %H:%M:%S")[0:6]))
        expiretion_date = rtime(long(time.mktime(d1.timetuple())+1e-6*d1.microsecond)*1000)
        ms = [str(m) for m in members]
        #gs = str(guests).split(';')
        if enable is not None:
            enable = True
        else:
            enable = False
        self.conn.updateShare(self.share.id, message, expiretion_date, ms, enable)
        
    def addComment(self, comment):
        self.conn.addComment(self.share.id, comment)

    def getAllShares(self):
        self.shares = self.conn.getAllShares()

    def getShares(self):
        self.ownShares = list(self.conn.getOwnShares())
        self.memberShares = list(self.conn.getMemberShares())
        self.oshSize = len(self.ownShares)
        self.mshSize = len(self.memberShares)

    def getComments(self, share_id):
        self.comments = list(self.conn.getComments(share_id))
        self.cmSize = len(self.comments)

    def getShare(self, share_id):
        self.membersInShare = list(self.conn.getAllMembers(share_id))
        #self.guestsInShare = ";".join(self.conn.getAllGuests(share_id))
        self.allInShare = list(self.conn.getAllUsers(share_id))

    def loadShareContent(self, share_id):
        content = self.conn.getContents(share_id)
        
        imInShare = list()
        dsInShare = list()
        prInShare = list()

        for ex in content:
            if isinstance(ex._obj, omero.model.ImageI):
                imInShare.append(ex.id)
            elif isinstance(ex._obj, omero.model.DatasetI):
                dsInShare.append(ex.id)
            elif isinstance(ex._obj, omero.model.ProjectI):
                prInShare.append(ex.id)

        if len(imInShare) > 0: 
            self.imageInShare = list(self.conn.getSpecifiedImages(imInShare))
            self.imgSize = len(self.imageInShare)
        if len(dsInShare) > 0: 
            self.datasetInShare = list(self.conn.getSpecifiedDatasetsWithLeaves(dsInShare))
            self.dsSize = len(self.datasetInShare)
        if len(prInShare) > 0: 
            self.projectInShare = list(self.conn.getSpecifiedProjectsWithLeaves(prInShare))
            self.prSize = len(self.projectInShare)
        
        self.sizeOfShare = self.imgSize+self.dsSize+self.prSize
        
    def getShareActive(self, share_id):
        content = self.conn_share.getContents(share_id)
        self.membersInShare = list(self.conn.getAllMembers(share_id))
        #self.guestsInShare = ";".join(self.conn.getAllGuests(share_id))
        self.allInShare = self.conn.getAllUsers(share_id)
        imInShare = list()
        dsInShare = list()
        prInShare = list()

        for ex in content:
            if isinstance(ex._obj, omero.model.ImageI):
                imInShare.append(ex.id)
            elif isinstance(ex._obj, omero.model.DatasetI):
                dsInShare.append(ex.id)
            elif isinstance(ex._obj, omero.model.ProjectI):
                prInShare.append(ex.id)
        
        if len(imInShare) > 0:
            self.imageInShare = list(self.conn_share.getSpecifiedImages(imInShare))
        if len(dsInShare) > 0:
            self.datasetInShare = list(self.conn_share.loadCustomHierarchy("Dataset", dsInShare))
        if len(prInShare) > 0:
            self.projectInShare = list(self.conn_share.loadCustomHierarchy("Project", prInShare))

# ### Test code below this line ###

if __name__ == '__main__':
    print "share"
