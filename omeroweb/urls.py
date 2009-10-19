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

import os.path

from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve

from omeroweb.webadmin.models import Gateway
from omeroweb.feedback.models import EmailTemplate

# make admin enable
admin.autodiscover()
admin.site.register(Gateway)
admin.site.register(EmailTemplate)

# error handler
handler404 = "omeroweb.feedback.views.handler404"
handler500 = "omeroweb.feedback.views.handler500"


# url patterns
urlpatterns = patterns('',

    # admin panel support
    (r'^admin/(.*)', admin.site.root),
    # Require link to admin media
    url( r'^admin_static/(?P<path>.*)$', serve ,{ 'document_root': os.path.join(os.path.dirname(os.path.realpath(admin.__file__)), 'media').replace('\\','/') }, name="admin_static" ),    
    (r'^webgateway/appmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'webgateway/media')}),
    
    (r'(?i)^webadmin/', include('omeroweb.webadmin.urls')),
    (r'(?i)^webclient/', include('omeroweb.webclient.urls')),
    (r'(?i)^feedback/', include('omeroweb.feedback.urls')),
    (r'(?i)^webgateway/', include('omeroweb.webgateway.urls')),
    
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/webadmin/static/images/ome.ico'}),

)
