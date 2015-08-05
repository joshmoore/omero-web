//
// Copyright (C) 2013-2014 University of Dundee & Open Microscopy Environment.
// All rights reserved.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

// Events
// 1) Item removed from the view (either deleted/moved in the tree or in the centre)
// 2) Item added to the view (either created/copied/moved in the tree or in the centre)
// 3) Selection changed in the tree or in the centre

/*global OME:true */
if (typeof OME === "undefined") {
    OME = {};
}

OME.multi_key = function() {
    if (navigator.appVersion.indexOf("Mac")!=-1) {
        return "meta";
    } else {
        return "ctrl";
    }
};

OME.getURLParameter = function(key) {
    /* Return single value for parameter with specified key
     * Does not handle multi-value parameters
     * Returns false if there are no parameters or it is not present
    */

    // If there are no parameters, just return false
    if (window.location.search.length === 0) {
        return false;
    }

    // Remove the leading '?'
    var search = window.location.search.substring(1);

    // Break them up
    var searchParams = search.split('&');

    for (var i = 0; i < searchParams.length; i++) {
        var paramSplit = searchParams[i].split('=');
        if (paramSplit[0] === key) {
            return paramSplit[1];
        }
    }
    return false;
};

jQuery.fn.hide_if_empty = function() {
    if ($(this).children().length === 0) {
        $(this).hide();
    } else {
        $(this).show();
    }
  return this;
};

// Function to enable measuring of a specific text element in jquery
$.fn.textWidth = function(text, font) {
    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').appendTo(document.body);
    var htmlText = text || this.val() || this.text();
    htmlText = $.fn.textWidth.fakeEl.text(htmlText).html(); //encode to Html
    htmlText = htmlText.replace(/\s/g, "&nbsp;"); //replace trailing and leading spaces
    $.fn.textWidth.fakeEl.html(htmlText).css('font', font || this.css('font'));
    return $.fn.textWidth.fakeEl.width();
};

// called from OME.tree_selection_changed() below
OME.handle_tree_selection = function(data, event) {

    var selected;
    if (typeof data != 'undefined') {
        selected = data.selected;
    }

    // Update the DOM recorded selection
    OME.writeSelectedObjs(selected);

    // Trigger selection changed event
    $("body").trigger("selection_change.ome", data);

    // Instead of using selection_change.ome to trigger syncThumbSelection
    // and update_thumbnails_panel, just run them instead

    // Check the functions exist, they might not if the central panel has not been loaded
    if (typeof(syncThumbSelection) === "function") {
        // safe to use the function
        syncThumbSelection(data, event);
    }
    if (typeof(update_thumbnails_panel) === "function") {
        // safe to use the function
        update_thumbnails_panel(event, data);
    }
};

// called on selection and deselection changes in jstree
OME.tree_selection_changed = function(data, evt) {
    // handle case of deselection immediately followed by selection - Only fire on selection
    if (typeof OME.select_timeout != 'undefined') {
        clearTimeout(OME.select_timeout);
    }
    OME.select_timeout = setTimeout(function() {
        OME.handle_tree_selection(data, evt);
    }, 10);
};

// Short-cut to setting selection to [], with option to force refresh.
// (by default, center panel doesn't clear when nothing is selected)
OME.clear_selected = function(force_refresh) {
    var refresh = (force_refresh === true);
    $("body")
        .data("selected_objects.ome", [])
        .trigger("selection_change.ome", [refresh]);
};

// select all images from the specified fileset (if currently visible)
OME.select_fileset_images = function(filesetId) {
    var datatree = $.jstree.reference('#dataTree');
    // This is only used when deleting filesets to select them all
    // Fundamentally it can not really work as the images may have
    // been split into many datasets. Given that it doesn't really
    // work, just select visual fields which are in the fileset
    $("#dataTree li[data-fileset="+filesetId+"]").each(function(){
        datatree.select_node(this);
    });
};

// actually called when share is edited, to refresh right-hand panel
OME.share_selection_changed = function(share_id) {
    $("body").trigger("selection_change.ome");
};


// Standard ids are in the form TYPE-ID, web extensions may add an
// additional -SUFFIX
OME.table_selection_changed = function($selected) {
    //TODO Use write select_objs function.
    // Guess this is for search and such where there is no tree?
    var selected_objs = [];
    if (typeof $selected != 'undefined') {
        $selected.each(function(i){
            var id_split = this.id.split('-');
            var id_obj = id_split.slice(0, 2).join('-');
            var id_suffix = id_split.slice(2).join('-');
            selected_objs.push( {"id":id_obj, "id_suffix":id_suffix} );
        });
    }
    $("body")
        .data("selected_objects.ome", selected_objs)
        .trigger("selection_change.ome");
};

// handles selection for 'clicks' on table (search, history & basket)
// including multi-select for shift and meta keys
OME.handleTableClickSelection = function(event) {

    var $clickedRow = $(event.target).parents('tr:first');
    var rows = $("table#dataTable tbody tr");
    var selIndex = rows.index($clickedRow.get(0));

    if ( event.shiftKey ) {
        // get existing selected items
        var $s = $("table#dataTable tbody tr.ui-selected");
        if ($s.length === 0) {
            $clickedRow.addClass("ui-selected");
            OME.table_selection_changed($clickedRow);
            return;
        }
        var sel_start = rows.index($s.first());
        var sel_end = rows.index($s.last());

        // select all rows between new and existing selections
        var new_start, new_end;
        if (selIndex < sel_start) {
            new_start = selIndex;
            new_end = sel_start;
        } else if (selIndex > sel_end) {
            new_start = sel_end+1;
            new_end = selIndex+1;
        // or just from the first existing selection to new one
        } else {
            new_start = sel_start;
            new_end = selIndex;
        }
        for (var i=new_start; i<new_end; i++) {
            rows.eq(i).addClass("ui-selected");
        }
    }
    else if (event.metaKey) {
        if ($clickedRow.hasClass("ui-selected")) {
            $clickedRow.removeClass("ui-selected");
        }
        else {
            $clickedRow.addClass("ui-selected");
        }
    }
    else {
        rows.removeClass("ui-selected");
        $clickedRow.addClass("ui-selected");
    }
    // update right hand panel etc
    OME.table_selection_changed($("table#dataTable tbody tr.ui-selected"));
};

// called from click events on plate. Selected wells
OME.well_selection_changed = function($selected, well_index, plate_class) {
    //TODO Use write selected_objs function
    var selected_objs = [];
    $selected.each(function(i){
        selected_objs.push( {"id":$(this).attr('id').replace("=","-"),
                "rel":$(this).attr('rel'),
                "index":well_index,
                "class":plate_class} );     // assume every well has same permissions as plate
    });

    $("body")
        .data("selected_objects.ome", selected_objs)
        .trigger("selection_change.ome");
};


// This is called by the Pagination controls at the bottom of icon or table pages.
OME.doPagination = function(page) {
    var datatree = $.jstree.reference('#dataTree');

    var $container = $("#content_details");
    var containerId = $container.data('id');
    var containerType = $container.data('type');
    var containerPath = $container.data('path');
    containerPath = JSON.parse(containerPath);
    var containerNode = datatree.find_omepath(containerPath);

    if (!containerNode) {
        console.log('WARNING: Had to guess container');
        containerNode = OME.getTreeBestGuess(containerType, containerId);
    }

    // Set the page for that node in the tree and reload the tree section
    datatree.change_page(containerNode, page);
    // Reselect the same node to trigger update
    datatree.deselect_all(true);
    datatree.select_node(containerNode);

    return false;
};



// handle deleting of Tag, File, Comment
// on successful delete via AJAX, the parent .domClass is hidden
OME.removeItem = function(event, domClass, url, parentId, index) {
    var removeId = $(event.target).attr('id');
    var dType = removeId.split("-")[1]; // E.g. 461-comment
    // /webclient/action/remove/comment/461/?parent=image-257
    var $parent = $(event.target).parents(domClass);
    var $annContainer = $parent.parent();
    var r = 'Remove ';
    if (dType === 'comment') r = 'Delete ';
    var confirm_remove = OME.confirm_dialog(r + dType + '?',
        function() {
            if(confirm_remove.data("clicked_button") == "OK") {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: {'parent':parentId, 'index':index},
                    dataType: 'json',
                    success: function(r){
                        if(eval(r.bad)) {
                            OME.alert_dialog(r.errs);
                        } else {
                            // simply remove the item (parent class div)
                            //console.log("Success function");
                            $parent.remove();
                            $annContainer.hide_if_empty();
                        }
                    }
                });
            }
        }
    );
    return false;
};

OME.deleteItem = function(event, domClass, url) {
    var deleteId = $(event.target).attr('id');
    var dType = deleteId.split("-")[1]; // E.g. 461-comment
    // /webclient/action/delete/file/461/?parent=image-257
    var $parent = $(event.target).parents("."+domClass);
    var $annContainer = $parent.parent();
    var confirm_remove = OME.confirm_dialog('Delete '+ dType + '?',
        function() {
            if(confirm_remove.data("clicked_button") == "OK") {
                $.ajax({
                    type: "POST",
                    url: url,
                    dataType:'json',
                    success: function(r){
                        if(eval(r.bad)) {
                            OME.alert_dialog(r.errs);
                        } else {
                            // simply remove the item (parent class div)
                            $parent.remove();
                            $annContainer.hide_if_empty();
                            window.parent.OME.refreshActivities();
                        }
                    }
                });
            }
        }
    );
    event.preventDefault();
    return false;
};

// Used to filter annotations in the metadata_general and batch_anntotate panels.
// Assumes a single #annotationFilter select on the page.
OME.filterAnnotationsAddedBy = function() {
    var $this = $("#annotationFilter"),
        val = $this.val(),
        userId = $this.attr('data-userId');

    // select made smaller if only 'Show all' text
    if (val === "all") {
        $this.css('width', '80px');
    } else {
        $this.css('width', '180px');
    }

    $('.tag_annotation_wrapper, .keyValueTable, .file_ann_wrapper, .ann_comment_wrapper, #custom_annotations tr')
            .each(function() {
        var $ann = $(this),
            addby = $ann.attr('data-added-by').split(",");
        var show = false;
        switch (val) {
            case "me":
                show = ($.inArray(userId, addby) > -1);
                break;
            case "others":
                for (var i=0; i<addby.length; i++) {
                    if (addby[i] !== userId) {
                        show = true;
                    }
                }
                break;
            default:    // 'all'
                show = true;
        }
        if (show) {
            $ann.show();
        } else {
            $ann.hide();
        }
    });
};

// More code that is shared between metadata_general and batch_annotate panels
// Called when panel loaded. Does exactly what it says on the tin.
OME.initToolbarDropdowns = function() {
    // -- Toolbar buttons - show/hide dropdown options --
    $(".toolbar_dropdown ul").css('visibility', 'hidden');
    // show on click
    var $toolbar_dropdownlists = $(".toolbar_dropdown ul");
    $(".toolbar_dropdown button").click(function(e) {
        // hide any other lists that might be showing...
        $toolbar_dropdownlists.css('visibility', 'hidden');
        // then show this one...
        $("ul", $(this).parent()).css('visibility', 'visible');
        e.preventDefault();
        return false;
    });
    // on hover-out, hide drop-down menus
    $toolbar_dropdownlists.hover(function(){}, function(){
        $(this).css('visibility', 'hidden');
    });

    // For Figure scripts, we need a popup:
    $("#figScriptList li a").click(function(event){
        if (!$(this).parent().hasClass("disabled")) {
            OME.openScriptWindow(event, 800, 600);
        }
        event.preventDefault();
        return false;
    });
};

// Simply add query to thumbnail src to force refresh.
// By default we do ALL thumbnails, but can also specify ID
OME.refreshThumbnails = function(options) {
    options = options || {};
    var rdm = Math.random(),
        thumbs_selector = "#dataIcons img",
        search_selector = ".search_thumb",
        spw_selector = "#spw img";
    // handle Dataset thumbs, search rusults and SPW thumbs
    if (options.imageId) {
        thumbs_selector = "#image_icon-" + options.imageId + " img";
        search_selector = "#image-" + options.imageId + " img.search_thumb";
        spw_selector += "#image-" + options.imageId;
    }
    $(thumbs_selector + ", " + spw_selector + ", " + search_selector).each(function(){
        var $this = $(this),
            base_src = $this.attr('src').split('?')[0];
        $this.attr('src', base_src + "?_="+rdm);
    });

    // Update viewport via global variable
    if (!options.ignorePreview && OME.preview_viewport && OME.preview_viewport.loadedImg.id) {
        OME.preview_viewport.load(OME.preview_viewport.loadedImg.id);
    }
};


// Handle deletion of selected objects in jsTree in container_tags.html and containers.html
OME.handleDelete = function() {
    var datatree = $.jstree._focused();
    var selected = datatree.get_selected();

    var del_form = $( "#delete-dialog-form" );
    del_form.dialog( "open" )
        .removeData("clicked_button");
    // clear previous stuff from form
    $.removeData(del_form, "clicked_button");
    $("#delete_contents_form").show();
    del_form.unbind("dialogclose");
    del_form.find("input[type='checkbox']").prop('checked', false);

    // set up form - process all the objects for data-types and children
    var ajax_data = [];
    var q = false;
    var dtypes = {};
    var first_parent;   // select this when we're done deleting
    var notOwned = false;
    selected.each(function (i) {
        if (!first_parent) first_parent = datatree._get_parent(this);
        var $this = $(this);
        ajax_data[i] = $this.attr('id').replace("-","=");
        var dtype = $this.attr('rel');
        if (dtype in dtypes) dtypes[dtype] += 1;
        else dtypes[dtype] = 1;
        if (!q && $this.attr('rel').indexOf('image')<0) q = true;
        console.log($this, $this.hasClass('isOwned'));
        if (!$this.hasClass('isOwned')) notOwned = true;
    });
    if (notOwned) {
        $("#deleteOthersWarning").show();
    } else {
        $("#deleteOthersWarning").hide();
    }
    var type_strings = [];
    for (var key in dtypes) {
        if (key === "acquisition") key = "Plate Run";
        type_strings.push(key.capitalize() + (dtypes[key]>1 && "s" || ""));
    }
    var type_str = type_strings.join(" & ");    // For delete dialog: E.g. 'Project & Datasets'
    $("#delete_type").text(type_str);
    if (!q) $("#delete_contents_form").hide();  // don't ask about deleting contents

    // callback when delete dialog is closed
    del_form.bind("dialogclose", function(event, ui) {
        if (del_form.data("clicked_button") == "Yes") {
            var delete_anns = $("#delete_anns").prop('checked');
            var delete_content = true;      // $("#delete_content").prop('checked');
            if (delete_content) ajax_data[ajax_data.length] = 'child=true';
            if (delete_anns) ajax_data[ajax_data.length] = 'anns=true';
            var url = del_form.attr('data-url');
            datatree.deselect_all();
            $.ajax({
                async : false,
                url: url,
                data : ajax_data.join("&"),
                dataType: "json",
                type: "POST",
                success: function(r){
                    if(eval(r.bad)) {
                          $.jstree.rollback(data.rlbk);
                          alert(r.errs);
                      } else {
                          // If deleting 'Plate Run', clear selection
                          if (type_str.indexOf('Plate Run') > -1) {
                            OME.clear_selected(true);
                          } else {
                            // otherwise, select parent
                            OME.tree_selection_changed();   // clear center and right panels etc
                            first_parent.children("a").click();
                          }
                          // remove node from tree
                          datatree.delete_node(selected);
                          OME.refreshActivities();
                      }
                },
                error: function(response) {
                    $.jstree.rollback(data.rlbk);
                    alert("Internal server error. Cannot remove object.");
                }
            });
        }
    });

    // Check if delete will attempt to partially delete a Fileset.
    var $deleteYesBtn = $('.delete_confirm_dialog .ui-dialog-buttonset button:nth-child(1)'),
        $deleteNoBtn = $('.delete_confirm_dialog .ui-dialog-buttonset button:nth-child(2) span'),
        filesetCheckUrl = del_form.attr('data-fileset-check-url');
    $.get(filesetCheckUrl + "?" + OME.get_tree_selection(), function(html){
        if($('div.split_fileset', html).length > 0) {
            var $del_form_content = del_form.children().hide();
            del_form.append(html);
            $deleteYesBtn.hide();
            $deleteNoBtn.text("Cancel");
            // On dialog close, clean-up what we changed above
            del_form.bind("dialogclose", function(event, ui) {
                $deleteYesBtn.show();
                $deleteNoBtn.text("No");
                $("#chgrp_split_filesets", del_form).remove();
                $del_form_content.show();
            });
        }
    });
};

OME.nodeHasPermission = function(node, permission) {
    /*
    * Check the permissions on a node
    */

    // Require that all nodes have the necessary permissions
    if ($.isArray(node)) {
        for (var index in node) {
            if (!OME.nodeHasPermission(node[index], permission)) {
                return false;
            }
        }
        // All must have had the permission
        return true;
    }

    if (permission === 'isOwned') {
        if (node.data.obj.hasOwnProperty('ownerId') && node.data.obj.ownerId === currentUserId()) {
            return node.data.obj.isOwned;
        } else if (node.type === 'experimenter' && node.data.id == currentUserId()) {
            return true;
        }
        return false;
    }

    // Check if the node data has permissions data
    if (node.data.obj.hasOwnProperty('permsCss')) {
        var perms = node.data.obj.permsCss;
        // Determine if this node has this permission
        if (perms.indexOf(permission) > -1) {
            return true;
        }
    }
    return false;
};


OME.writeSelectedObjs = function(selected_tree_nodes, selected_icons) {
/***
 * Write the current selection to the dom
*/

    var selected_objs = [];
    if (selected_tree_nodes !== undefined && selected_tree_nodes.length > 0) {
        var inst = $.jstree.reference('#dataTree');
        $.each(selected_tree_nodes, function(index, val) {
            var node = inst.get_node(val);
            var oid = node.type + '-' + node.data.obj.id;
            var selected_obj = {
                'id': oid,
                'rel': node.type,
                'class': node.data.obj.permsCss
            };
            // If it's an image it will have a filesetId
            if (node.type === 'image') {
                selected_obj['fileset'] = node.data.obj.filesetId;
            }

            selected_objs.push(selected_obj);
        });
    } else if (selected_icons !== undefined && selected_icons.length > 0) {
        selected_icons.each(function(index, el) {
            var $el = $(el);
            var oid = $el.data('type') + '-' + $el.data('id');
            //TODO Fill in class
            var selected_obj = {
                'id': oid,
                'rel': $el.data('type'),
                'class': $el.data('perms')
            };

            // If it's an image it will have a filesetId
            if ($el.data('type') === 'image') {
                selected_obj['fileset'] = $el.data('fileset');
            }

            selected_objs.push(selected_obj);
        });
    }

    $("body").data("selected_objects.ome", selected_objs);
};

OME.getTreeBestGuess = function(targetType, targetId) {
    /***
    * Get a tree node that is of the correct type and id
    * that is in the current selection hierarchy
    * This can mean that the target is selected, an ancestor is selected,
    * or that it has a selected descendant
    ***/
    var datatree = $.jstree.reference('#dataTree');

    // Find the matching child nodes from the tree
    // Locate any matching nodes and then find the one (or take the first
    // as there could be multiple) that has the currently selected parent
    var locatedNodes = datatree.locate_node(targetType + '-' + targetId);

    if (!locatedNodes) {
        datatree.deselect_all();
        return;
    }

    // Get the current jstree selection
    var selectedNodes = datatree.get_selected();
    var node;
    var parentNodeIds = [];

    var traverseUp = function(nodeId) {
        // Got to the root, give up
        if (nodeId === '#') {
            return false;
        } else {
            // Found a node that was selected
            if (selectedNodes.indexOf(nodeId) != -1) {
                return true;
            // Not found, recurse upwards
            } else {
                return traverseUp(datatree.get_parent(nodeId));
            }
        }
    };

    var traverseDown = function(nodeId) {
        if (selectedNodes.indexOf(nodeId) != -1) {
            return true;
        }

        var n = datatree.get_node(nodeId);
        // Got to a leaf, give up
        if (n.type === 'image'){
            return false;
        // Not found, recurse downwards
        } else {
            var ret = false;
            $.each(n.children, function(index, val) {
                 if (traverseDown(val)) {
                    ret = true;
                    // Breat out of each
                    return false;
                 }
            });
            return ret;
        }
    };

    // Find a node that matches our target that has a selected parent
    // Keep in mind that this will return the first potential node which
    // has a selected parent.
    // WARNING: This may not give expected results with multiselects
    $.each(locatedNodes, function(index, val) {
         if (traverseUp(val.id)) {
            node = val;
            // Break out of each
            return false;
         }
         // It is possible that the selection is below the item we are looking for
         // so look for a selection below as well to indicate the best guess
         if (val.type != 'image' && traverseDown(val.id)) {
            node = val;
            // Break out of each
            return false;
         }
    });

    return node;

};

OME.getTreeImageContainerBestGuess = function(imageId) {

    var datatree = $.jstree.reference('#dataTree');
    var selectType = 'image';

    // Find the matching child nodes from the tree
    // Locate any matching nodes and then find the one (or take the first
    // as there could be multiple) that has the currently selected parent
    var locatedNodes = datatree.locate_node(selectType + '-' + imageId);

    if (!locatedNodes) {
        datatree.deselect_all();
        return;
    }

    // Get the current jstree selection
    var selectedNodes = datatree.get_selected(true);
    var containerNode;
    var parentNodeIds = [];

    // Double check that it is either a single dataset selection or a multi
    // image selection. Get all the possible parent nodes
    // TODO What about orphaned selection?
    if (selectedNodes.length === 1 && selectedNodes[0].type === 'dataset') {
        parentNodeIds.push(selectedNodes[0].id);
    } else if (selectedNodes.length >= 1 && selectedNodes[0].type === 'image') {
        // Get the parents of the selected nodes
        $.each(selectedNodes, function(index, selectedNode) {
            parentNodeIds.push(datatree.get_parent(selectedNode));
        });
    }

    // webclient allows multiselect which is not bounded by a
    // single container. Take the first located node that has a correct
    // parent and has a selection.

    // Get the first of the located nodes that has one of these selected nodes as a parent
    $.each(locatedNodes, function(index, locatedNode) {
        var locatedNodeParentId = datatree.get_parent(locatedNode);

        // If there was no selection, just guess that the first parent we come to is ok
        if (parentNodeIds.length === 0) {
            containerNode = datatree.get_node(locatedNodeParentId);
            // Break out of $.each
            return false;

        // If this located node's parent is valid
        } else if ($.inArray(locatedNodeParentId, parentNodeIds) != -1) {
            // This is the container we need
            containerNode = datatree.get_node(locatedNodeParentId);
            // Break out of $.each
            return false;
        }

    });

    return containerNode;
};

jQuery.fn.tooltip_init = function() {
    $(this).tooltip({
        items: '.tooltip',
        content: function() {
            return $(this).parent().find("span.tooltip_html").html();
        },
        track: true,
        show: false,
        hide: false
    });
  return this;
};
