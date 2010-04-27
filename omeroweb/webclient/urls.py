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
from django.views.static import serve

from omeroweb.webclient import views
#from omeroweb.webclient.feeds import RssShareFeed, AtomShareFeed

'''feeds = {
    'rss': RssShareFeed,
    'atom': AtomShareFeed,
}'''

urlpatterns = patterns('',
    
    url( r'^$', views.index, name="webindex" ),
    # render main template
    url( r'^(?P<menu>((?i)userdata|public|history|search|importer|help|usertags))/$', views.load_template, name="load_template" ),

    url( r'^context/$', views.index_context, name="index_context" ),
    url( r'^last_imports/$', views.index_last_imports, name="index_last_imports" ),
    url( r'^most_recent/$', views.index_most_recent, name="index_most_recent" ),
    url( r'^tag_cloud/$', views.index_tag_cloud, name="index_tag_cloud" ),
    
    url( r'^login/$', views.login, name="weblogin" ),
    url( r'^logout/$', views.logout, name="weblogout" ),
    url( r'^active_group/$', views.change_active_group, name="change_active_group" ),
    
    url ( r'^myaccount/(?:(?P<action>((?i)save))/)?$', views.manage_myaccount, name="myaccount"),
    url ( r'^upload_myphoto/(?:(?P<action>((?i)upload|crop|editphoto))/)?$', views.upload_myphoto, name="upload_myphoto"),
    
    # load basket
    url( r'^basket/empty/$', views.empty_basket, name="empty_basket"),
    url( r'^basket/update/$', views.update_basket, name="update_basket"),
    url( r'^basket/(?:(?P<action>[a-zA-Z]+)/)?$', views.basket_action, name="basket_action"),
    
    # loading data
    url( r'^load_data/(?P<o1_type>((?i)orphaned))/$', views.load_data, name="load_data_ajax" ),
    
    url( r'^load_data/(?:(?P<o1_type>((?i)project|dataset|image|screen|plate|well))/)?(?:(?P<o1_id>[0-9]+)/)?(?:(?P<o2_type>((?i)dataset|image|plate|well))/)?(?:(?P<o2_id>[0-9]+)/)?(?:(?P<o3_type>((?i)image|well))/)?(?:(?P<o3_id>[0-9]+)/)?$', views.load_data, name="load_data" ),    
    
    url( r'^load_data/(?P<o1_type>((?i)project|dataset|image|screen|plate|well))/(?P<o1_id>[0-9]+)/$', views.load_data, name="load_data_t_id" ),
    url( r'^load_data/(?P<o1_type>((?i)project|dataset|screen|plate))/(?P<o1_id>[0-9]+)/(?P<o2_type>((?i)dataset|image|plate|well))/(?P<o2_id>[0-9]+)/$', views.load_data, name="load_data_t_id_t_id" ),
    url( r'^load_data/(?P<o1_type>((?i)project|screen))/(?P<o1_id>[0-9]+)/(?P<o2_type>((?i)dataset|plate))/(?P<o2_id>[0-9]+)/(?P<o3_type>((?i)image|well))/(?P<o3_id>[0-9]+)/$', views.load_data, name="load_data_t_id_t_id_t_id" ),
    
    # load history
    url( r'^load_calendar/(?:(\d{4})/(\d{1,2})/)?$', views.load_calendar, name="load_calendar"),
    url( r'^load_history/(\d{4})/(\d{1,2})/(\d{1,2})/$', views.load_history, name="load_history"),
    url( r'^load_searching/(?:(?P<form>((?i)form)))/$', views.load_searching, name="load_searching"),
    
    
    # others
    url( r'^hierarchy/(?:(?P<o_type>[a-zA-Z]+)/(?P<o_id>[0-9]+)/)?$', views.load_hierarchies, name="load_hierarchies" ),
    url( r'^metadata_details/(?P<c_type>[a-zA-Z]+)/(?P<c_id>[0-9]+)/(?:(?P<index>[0-9]+)/)?$', views.load_metadata_details, name="load_metadata_details" ),
    url( r'^metadata_details/multiaction/$', views.load_metadata_details_multi, name="load_metadata_details_multi" ),
    
    url( r'^action/(?P<action>[a-zA-Z]+)/(?:(?P<o_type>[a-zA-Z]+)/)?(?:(?P<o_id>[0-9]+)/)?$', views.manage_action_containers, name="manage_action_containers" ),
    url( r'^annotation/(?P<action>[a-zA-Z]+)/(?P<iid>[0-9]+)/$', views.download_annotation, name="download_annotation" ),
    
    url( r'^load_tags/(?:(?P<o_type>((?i)tag|dataset))/(?P<o_id>[0-9]+)/)?$', views.load_data_by_tag, name="load_data_by_tag" ),
    url( r'^autocompletetags/$', views.autocomplete_tags, name="autocomplete_tags" ),
    
    # render thumbnails
    url( r'^render_thumbnail/(?P<iid>[0-9]+)/(?:(?P<share_id>[0-9]+)/)?$', views.render_thumbnail, name="render_thumbnail" ),
    url( r'^render_thumbnail/size/(?P<size>[0-9]+)/(?P<iid>[0-9]+)/(?:(?P<share_id>[0-9]+)/)?$', views.render_thumbnail_resize, name="render_thumbnail_resize" ),
    url( r'^render_thumbnail/big/(?P<iid>[0-9]+)/$', views.render_big_thumbnail, name="render_big_thumbnail" ),
    url( r'^public/$', views.manage_shares, name="manage_shares" ),
    url( r'^public/(?P<action>[a-zA-Z]+)/(?:(?P<sid>[0-9]+)/)?$', views.manage_share, name="manage_share" ),
    url( r'^public_content/(?P<share_id>[0-9]+)/$', views.load_share_content, name="load_share_content" ),
    url( r'^public_owner_content/(?P<share_id>[0-9]+)/$', views.load_share_owner_content, name="load_share_owner_content" ),
    
    url( r'^clipboard/$', views.update_clipboard, name="update_clipboard"),
    
    
    url( r'^import/$', views.importer, name="importer"),
    url( r'^upload/$', views.flash_uploader, name="flash_uploader"), 
    
    url( r'^help/$', views.help, name="help" ),
    
    url( r'^myphoto/$', views.myphoto, name="myphoto"),
    url( r'^userphoto/(?P<oid>[0-9]+)/$', views.load_photo, name="load_photo"),
    url( r'^(?:(?P<share_id>[0-9]+)/)?render_image/(?P<iid>[0-9]+)/(?P<z>[0-9]+)/(?P<t>[0-9]+)/$', views.render_image, name="render_image"),
    url( r'^(?:(?P<share_id>[0-9]+)/)?img_detail/(?P<iid>[0-9]+)/$', views.image_viewer, name="image_viewer"),
    url( r'^(?:(?P<share_id>[0-9]+)/)?imgData/(?P<iid>[0-9]+)/$', views.imageData_json, name="imageData_json"),
    
    url(r'^(?:(?P<share_id>[0-9]+)/)?render_row_plot/(?P<iid>[^/]+)/(?P<z>[^/]+)/(?P<t>[^/]+)/(?P<y>[^/]+)/(?:(?P<w>[^/]+)/)?$', views.render_row_plot, name="render_row_plot"),
    url(r'^(?:(?P<share_id>[0-9]+)/)?render_col_plot/(?P<iid>[^/]+)/(?P<z>[^/]+)/(?P<t>[^/]+)/(?P<x>[^/]+)/(?:(?P<w>[^/]+)/)?$', views.render_col_plot, name="render_col_plot"),
    url(r'^(?:(?P<share_id>[0-9]+)/)?render_split_channel/(?P<iid>[^/]+)/(?P<z>[^/]+)/(?P<t>[^/]+)/$', views.render_split_channel, name="render_split_channel"),

    url( r'^spellchecker/$', views.spellchecker, name="spellchecker"), 
    
    #( r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',{'feed_dict': feeds}),
    
    #test ROI
    url( r'^test/$', views.test, name="test"), 
    url( r'^histogram/(?P<oid>[0-9]+)/$', views.histogram, name="histogram"), 
    
)
