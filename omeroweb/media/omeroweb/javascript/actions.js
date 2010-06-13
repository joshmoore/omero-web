function isCheckedById(name) { 
    var checked = $("input[name='"+name+"']:checked").length; 
    if (checked == 0) { return false; } else { return true; } 
}

var calculateCartTotal = function(total)
{
    $('#cartTotal').html(total);
};

function manyToAnnotation(){
    if (!isCheckedById("image") && !isCheckedById("dataset") && !isCheckedById("project") && !isCheckedById("well") && !isCheckedById("plate") && !isCheckedById("screen")) {
        alert ("Please select at least one image. Currently you cannot add other objects to basket."); 
    } else { 
        var productListQuery = "/webclient/metadata_details/multiaction/annotatemany/?";
        $("input[type='checkbox']:checked").each(function() {
            if(this.checked) {
                productListQuery += "&"+this.name+"="+this.id;
            }
        });
        
        var h = $(window).height()-200;
        $("#right_panel").show();
        $("#swapMeta").html('<img tabindex="0" src="/appmedia/omeroweb/images/tree/spacer.gif"" class="collapsed-right" id="lhid_trayhandle_icon_right">'); 
        $("div#metadata_details").html('<iframe width="370" height="'+(h+31)+'" src="'+productListQuery+'" id="metadata_details" name="metadata_details"></iframe>');
        $('iframe#metadata_details').load();
    }    
}

function manyAddToBasket() {     
    if (!isCheckedById("image")) {//&& !isCheckedById("dataset") && !isCheckedById("plate")) {
        alert ("Please select at least one image. Currently you cannot add other objects to basket."); 
    } else { 
        manyToBasket($("input[type='checkbox']:checked"));
    }
};

function toBasket (productType, productId) {
    if (productId == null) {
        alert("No object selected.")
    } else {
        $.ajax({
            type: "POST",
            url: "/webclient/basket/update/", //this.href,
            data: "action=add&productId="+productId+"&productType="+productType,
            contentType:'html',
            success: function(responce){
                if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                    alert(responce)
                } else {
                    calculateCartTotal(responce);
                }
            },
            error: function(responce) {
                alert(responce)
                alert("Internal server error. Cannot add to basket.")
            }
        });
    }
};

function manyToBasket (productArray) { 
    var productListQuery = "action=addmany";
    productArray.each(function() {
        if(this.checked) {
            productListQuery += "&"+this.name+"="+this.id;
        }
    });
    
    $.ajax({
        type: "POST",
        url: "/webclient/basket/update/", //this.href,
        data: productListQuery,
        contentType:'html',
        success: function(responce){
            if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                alert(responce)
            } else {
                calculateCartTotal(responce);
            }
        },
        error: function(responce) {
            alert("Internal server error. Cannot add to basket.")
        }
    });
};

function manyRemoveFromBasket() {     
    if (!isCheckedById("image")) {//&& !isCheckedById("dataset") && !isCheckedById("plate")) {
        alert ("Please select at least one image. Currently you cannot add other objects to basket."); 
    } else { 
        manyFromBasket($("input[type='checkbox']:checked"));
    }
};

function manyFromBasket(productArray) {
    var productListQuery = "action=delmany";
    productArray.each(function() {
        if(this.checked) {
            productListQuery += "&"+this.name+"="+this.id;
        }
    });
    
    $.ajax({
        type: "POST",
        url: "/webclient/basket/update/", //this.href,
        data: productListQuery,
        contentType:'html',
        cache:false,
        success: function(responce){
            if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                alert(responce)
            } else {
                window.location = "/webclient/basket/";
            }
        },
        error: function(responce) {
            alert("Internal server error. Cannot remove from basket.")
        }
    });
}

function manyUnlink(parent) { 
    if (!isCheckedById("dataset") && !isCheckedById("image") && !isCheckedById("plate")) {
        alert ("Please select at least one object"); 
    } else { 
        unlink($("input[type='checkbox']:checked"), parent);
    }
};

function selectAll() {
    $("INPUT[type='checkbox']").attr('checked', $('#checkAllAuto').is(':checked'));   
}

function unlink (productArray, parent) { 
    var productListQuery = "parent="+parent;
    productArray.each(function() {
        if(this.checked) {
            productListQuery += "&"+this.name+"="+this.id;
        }
    });
    $.ajax({
        type: "POST",
        url: "/webclient/action/removemany/", //this.href,
        data: productListQuery,
        contentType:'html',
        success: function(responce){
            if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                alert(responce)
            } else {
                window.location.replace("");
            }
        },
        error: function(responce) {
            alert("Internal server error. Cannot add to basket.")
        }
    });
};

function manyDelete() { 
    if (!isCheckedById("image") && !isCheckedById("plate")) {
        alert ("Please select at least one object"); 
    } else { 
        deleteItems($("input[type='checkbox']:checked"), parent);
    }
};

function deleteItems (productArray, parent) { 
    var productListQuery = "parent="+parent;
    productArray.each(function() {
        if(this.checked) {
            productListQuery += "&"+this.name+"="+this.id;
        }
    });
    $.ajax({
        type: "POST",
        url: "/webclient/action/deletemany/", //this.href,
        data: productListQuery,
        contentType:'html',
        success: function(responce){
            if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                alert(responce)
            } else {
                window.location.replace("");
            }
        },
        error: function(responce) {
            alert("Internal server error. Cannot add to basket.");
        }
    });
};

function deleteItem(productType, productId) {
    if ((productType == 'project' || productType == 'dataset' || productType == 'image' || productType == 'screen' || productType == 'plate' || productType == 'share') && productId > 0){
        if (confirm('Delete '+productType+'?')) {
            if ((productType == 'project' || productType == 'dataset' || productType == 'screen') && confirm('Also delete content?')) {
                all = 'all=on';
            } else {
                all = null;
            }
            $.ajax({
                type: "POST",
                url: "/webclient/action/delete/"+productType+"/"+productId+"/", //this.href,
                data: all,
                contentType:'html',
                success: function(responce){
                    if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                        alert(responce)
                    } else {
                        window.location.replace("");
                    }
                },
                error: function(responce) {
                    alert("Internal server error. Cannot add to basket.");
                }
            });
            
        }
    } 
}

function manyCopyToClipboard() { 
    if (isCheckedById("project") || isCheckedById("screen")) {
        alert ("You can only copy datasets, images or plates. Please uncheck projects and screens."); 
    } else if (!isCheckedById("dataset") && !isCheckedById("plate") && !isCheckedById("image")) {
        alert ("Please select at least one dataset, image or plate."); 
    } else if (isCheckedById("dataset") && isCheckedById("plate")) {
        alert ("Please select only datasets, images or plates."); 
    } else { 
        copyToClipboard($("input[type='checkbox']:checked"));
    }
};

function copyToClipboard (productArray) {
    var productListQuery = "action=copy";
    if (productArray.length > 0 ) {
        productArray.each(function() {
            if(this.checked) {
                productListQuery += "&"+this.name+"="+this.id;
            }
        });
    } else {
        productListQuery += "&"+productArray.name+"="+productArray.id;
    }
    $.ajax({
        type: "POST",
        url: "/webclient/clipboard/", //this.href,
        data: productListQuery,
        contentType:'html',
        success: function(responce) {
            if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                alert(responce)
            } else {
                alert(responce)
            }
        },
        error: function(responce) {
            alert("Internal server error. Cannot add to basket.")
        }
    });
};

function treeCopyToClipboard(productType, productId) {
    if (productId == null) {
        alert("No object selected.");
    } else {
        input = $('<input type="checkbox" checked/>').attr('name', productType).attr('id', productId).attr('class', 'hide');
        copyToClipboard(input);
    }
};

function pasteFromClipboard (destinationType, destinationId, url) {
    if (destinationId == null) {
        alert("No object selected.")
    } else {
        $.ajax({
            type: "POST",
            url: "/webclient/clipboard/", //this.href,
            data: "action=paste&destinationId="+destinationId+"&destinationType="+destinationType,
            contentType:'html',
            success: function(responce){
                if(responce.match(/(Error: ([a-z][A-Z]+))/gi)) {
                    alert(responce)
                } else {
                    window.location = url
                }
            },
            error: function(responce) {
                alert("Internal server error. Could not be pasted.")
            }
        });
    }
};


function cleanClipboard (productType, productId) {
    if (productId == null) {
        alert("No object selected.")
    } else {
        $.ajax({
            type: "POST",
            url: "/webclient/clipboard/", //this.href,
            data: "action=clean",
            contentType:'html',
            success: function(responce){
                alert(responce);
            },
            error: function(responce) {
                alert(responce)
            }
        });
    }
};

function changeView(view) { 
    var rel = $("div#content_details").attr('rel').split("-");
    if(rel=='orphaned') {
        $("div#content_details").html('<p>Loading data... please wait <img src="/appmedia/omeroweb/images/tree/spinner.gif"/></p>');
        $("div#content_details").load('/webclient/load_data/orphaned/?view='+view);
    } else {
        $("div#content_details").html('<p>Loading data... please wait <img src="/appmedia/omeroweb/images/tree/spinner.gif"/></p>');
        $("div#content_details").load('/webclient/load_data/dataset/'+rel[1]+'/?view='+view);
    }
    return false;
};

function openPopup(url) {
    owindow = window.open(url, 'anew', config='height=600,width=850,left=50,top=50,toolbar=no,menubar=no,scrollbars=yes,resizable=yes,location=no,directories=no,status=no');
    if(!owindow.closed) owindow.focus();
    return false;
}


function saveMetadata (image_id, metadata_type, metadata_value) {
    if (image_id == null) {
        alert("No image selected.")
    } else {
        $($('#id_'+metadata_type).parent()).append('<img src="/appmedia/omeroweb/images/tree/spinner.gif"/>');
        $.ajax({
            type: "POST",
            url: "/webclient/metadata/image/"+image_id+"/", //this.href,
            data: "matadataType="+metadata_type+"&metadataValue="+metadata_value,
            contentType:'html',
            cache:false,
            success: function(responce){
                $($('#id_'+metadata_type).parent().find('img')).remove()
            },
            error: function(responce) {
                $($('#id_'+metadata_type).parent().find('img')).remove()
                alert("Cannot save new value for '"+metadata_type+"'.")
            }
        });
    }
}

function editItem(type, item_id) {
    var h = $(window).height()-169;
    $("#right_panel").show();
    $("#swapMeta").html('<img tabindex="0" src="/appmedia/omeroweb/images/tree/spacer.gif" class="collapsed-right" id="lhid_trayhandle_icon_right">');
    $("div#metadata_details").html('<iframe width="370" height="'+h+'" src="/webclient/action/edit/'+type+'/'+item_id+'/" id="metadata_details" name="metadata_details"></iframe>');
    $('iframe#metadata_details').load();
    return false;
}

function doPagination(view, page) {
    var rel = $("div#content_details").attr('rel').split("-");
    $("div#content_details").html('<p>Loading data... please wait <img src="/appmedia/omeroweb/images/tree/spinner.gif"/></p>');
    $("div#content_details").load('/webclient/load_data/dataset/'+rel[1]+'/?view='+view+'&page='+page);
    return false;
}

function makeShare() {
    if (!isCheckedById("image")) {//&& !isCheckedById("dataset") && !isCheckedById("plate")) {
        alert ("Please select at least one image. Currently you cannot add other objects to basket."); 
    } else { 
        var productArray = $("input[type='checkbox']:checked");
        var productListQuery = "";
        if (productArray.length > 0 ) {
            productArray.each(function() {
                if(this.checked) {
                    productListQuery += "&"+this.name+"="+this.id;
                }
            });
        } else {
            productListQuery += "&"+productArray.name+"="+productArray.id;
        }
    }
    
    var h = $(window).height()-169;
    $("#right_panel").show();
    $("#swapMeta").html('<img tabindex="0" src="/appmedia/omeroweb/images/tree/spacer.gif" class="collapsed-right" id="lhid_trayhandle_icon_right">');
    $("div#metadata_details").html('<iframe width="370" height="'+h+'" src="/webclient/basket/toshare/?'+productListQuery+'" id="metadata_details" name="metadata_details"></iframe>');
    $('iframe#metadata_details').load();
    return false;
}

function makeDiscussion() {
    var h = $(window).height()-169;
    $("#right_panel").show();
    $("#swapMeta").html('<img tabindex="0" src="/appmedia/omeroweb/images/tree/spacer.gif" class="collapsed-right" id="lhid_trayhandle_icon_right">');
    $("div#metadata_details").html('<iframe width="370" height="'+h+'" src="/webclient/basket/todiscuss/" id="metadata_details" name="metadata_details"></iframe>');
    $('iframe#metadata_details').load();
    return false;
}
