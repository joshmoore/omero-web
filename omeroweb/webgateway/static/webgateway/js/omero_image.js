


(function(){

    function show_change(obj, val, klass) {
        if (obj.value != val) {
            $(obj).addClass(klass);
        } else {
            $(obj).removeClass(klass);
        }
    }
    function hidePicker () {
        $(".picker").get(0) && $(".picker").get(0).hide_picker && $(".picker").get(0).hide_picker();
        /*$('.picker-selected').html('&nbsp;');*/
    }

    window.resetRDCW = function (viewport) {
        viewport.reset_channels();
        syncRDCW(viewport);
    }

    window.resetImageDefaults = function (viewport, obj, callback) {
        var msg = '<h2>Resetting rendering settings</h2><ul><li>This will reset the image rendering settings to their original state at time of import.</li></ul>';
        var url = viewport.viewport_server + '/resetImgRDef/'+viewport.loadedImg.id+'/';
        gs_choiceModalJson(msg, [
                {label: 'ok', url: url, data: {full: true}},
                {label: 'cancel'}
            ],
            function(success, rv) {
                if (!rv) {
                    alert('Reset image defaults failed.');
                } else {
                    viewport.load(viewport.loadedImg.id, viewport.loadedImg.current.dataset_id);
                }
                if (callback) {
                    callback();
                }
            },
            {css: {width: '50%', left: '25%'}}
        );
        return false;
    }

    window.setImageDefaults = function (viewport, obj, callback, skip_apply) {
        if (!skip_apply) applyRDCW(viewport);
        var old = $(obj).html();
        gs_modalJson(viewport.viewport_server + '/saveImgRDef/'+viewport.loadedImg.id+'/?'+viewport.getQuery(true),
            {},
            function(success, rv) {
                $(obj).html(old).attr('disabled', false);
                if (!(success && rv)) {
                    alert('Setting image defaults failed.');
                }
                if (callback) {
                    callback();
                }
            });
        return false;
    }

    window.zindex_automator = function(klass, basez, wspace) {
        if (!wspace) {
            wspace = $(klass);
        }
        var sorter = function (a,b) {
            return parseInt(a.css('z-index'))-parseInt(b.css('z-index'));
        };
        var tofront = function (e) {
            var self = this;
            var z = basez;
            var objs = new Array();
            $(klass).each(function () {
                this != self && objs.push($(this));
            });
            $.each(objs.sort(sorter), function () {
                this.css('z-index', z);
                z++;
            });
            $(self).css('z-index', z);
        };
        $.each(wspace, function () {
            $(this).bind('opening', tofront);
            $(this).bind('mousedown', tofront);
        });
    }

    window.channelChange = function (ev, obj, idx, ch) {
        if (ch.active) {
            $('#wblitz-ch'+idx).addClass('pressed');
        } else {
            $('#wblitz-ch'+idx).removeClass('pressed');
        }
        //var t = $('#rd-wblitz-ch'+idx).get(0);
        //if (t != undefined) t.checked=ch.active;
        $('#wblitz-ch'+idx).css('background-color', ch.color).attr('title', ch.label);
    };

    window.syncChannelsActive = function(viewport) {
        var channels = viewport.getChannels();
        for (i=0; i<channels.length; i++) {
            $('#rd-wblitz-ch'+i).get(0).checked = channels[i].active;
        }
    }

    window.syncRDCW = function(viewport) {
        var cb;
        var channels = viewport.getChannels();
        for (i=0; i<channels.length; i++) {
            // $('#rd-wblitz-ch'+i).get(0).checked = channels[i].active;
            $('#wblitz-ch'+i+'-cwslider .ui-slider-range').css('background-color', toRGB(channels[i].color));
            var w = channels[i].window;
            $('#wblitz-ch'+i+'-cwslider')
                .slider( "option", "min", Math.min(w.min, w.start) )   // extend range if needed
                .slider( "option", "max", Math.max(w.max, w.end) );
                $('#wblitz-ch'+i+'-color').css('background-color', toRGB(channels[i].color));//$('#wblitz-ch'+i).css('background-color'));
                $('#wblitz-ch'+i+'-cw-start').val(channels[i].window.start).change();
                $('#wblitz-ch'+i+'-cw-end').val(channels[i].window.end).change();
        }
        hidePicker();

        // update disabled status of undo/redo buttons
        if (viewport.has_channels_undo()) {
            $('#rdef-undo-btn').removeAttr('disabled');
        } else {
            $('#rdef-undo-btn').attr('disabled', 'disabled');
        }
        if (viewport.has_channels_redo()) {
            $('#rdef-redo-btn').removeAttr('disabled');
        } else {
            $('#rdef-redo-btn').attr('disabled', 'disabled');
        }

        $('#rd-wblitz-rmodel').attr('checked', !viewport.isGreyModel());
        syncChannelsActive(viewport);
    }

    var on_batchCopyRDefs = false;
    // TODO: try not to rely on global variables!
    window.applyRDCW = function(viewport, final) {
        if (on_batchCopyRDefs) {
            return batchCopyRDefs_action('ok');
        }
        viewport.setModel($('#rd-wblitz-rmodel').get(0).checked?'c':'g');
        for (var i=0; i<viewport.getCCount(); i++) {
            viewport.setChannelActive(i, $('#rd-wblitz-ch'+i).get(0).checked, true);
            viewport.setChannelColor(i, $('#wblitz-ch'+i+'-color').css('background-color'), true);
            var noreload = ((i+1) < viewport.getCCount());    // prevent reload, except on the last loop
            viewport.setChannelWindow(i, $('#wblitz-ch'+i+'-cw-start').get(0).value, $('#wblitz-ch'+i+'-cw-end').get(0).value, noreload);
        }

        if (final) {
            viewport.forget_bookmark_channels();
            $('#rdef-postit').hide();
        }
        viewport.save_channels();
        syncRDCW(viewport);
    }

    /**
    * Gets called when an image is initially loaded.
    * This is the place to sync everything; rendering model, quality, channel buttons, etc.
    */
    window._refresh_cb = function (ev, viewport) {
        /* Sync inputs with initial values */

        $('#wblitz-rmodel').attr('checked', !viewport.isGreyModel());
        $('#wblitz-invaxis').attr('checked', viewport.loadedImg.rdefs.invertAxis);
        //$('#rd-wblitz-rmodel').attr('checked', !viewport.isGreyModel());

        var q = viewport.getQuality();
        if (q) {
            var qr = $('#wblitz-quality > [value="+q.toFixed(1)+"]');
            if (qr.length) {
                qr.attr('selected','selected');
            }
        }

        /* Prepare the channels box and the rendering definition for the channels */
        var box = $('#wblitz-channels-box');
        var channels = viewport.getChannels();
        box.empty();

        var doToggle = function(index) {
            return function() {
                viewport.toggleChannel(index);
            }
        }
        for (i=0; i<channels.length; i++) {
            $('<button id="wblitz-ch'+i+'"\
                class="squared' + (channels[i].active?' pressed':'') + '"\
                style="background-color: #'+channels[i].color+'"\
                title="'+channels[i].label+'"\
                >'+channels[i].label+'</button>')
            .appendTo(box)
            .bind('click', doToggle(i));
        }

        // disable 'split' view for single channel images.
        if (channels.length < 2) {
            $("input[value='split']").attr('disabled', 'disabled');
        }

        /* Image details */
        var tmp = viewport.getMetadata();
        $('#wblitz-image-name').html(tmp.imageName);
        $('#wblitz-image-description-content').html(tmp.imageDescription.replace(/\n/g, '<br />'));
        $('#wblitz-image-author').html(tmp.imageAuthor);
        $('#wblitz-image-pub').html(tmp.projectName);
        $('#wblitz-image-pubid').html(tmp.projectId);
        $('#wblitz-image-timestamp').html(tmp.imageTimestamp);

        $("#bulk-annotations").hide();
        $("#bulk-annotations").next().hide();
        if (tmp.wellId) {
            // Load bulk annotations for plate
            var onAnnotations = function(result) {
                if (result.data && result.data.rows) {
                    var table = $("#bulk-annotations").show().next().show().children("table");
                    for (var col in result.data.columns) {
                        var label = result.data.columns[col];
                        var value = '';
                        for (var row in result.data.rows) {
                          value += result.data.rows[row][col] + '<br />';
                        }
                        var row = $('<tr><td class="title"></td><td></td></tr>');
                        row.addClass(col % 2 == 1 ? 'odd' : 'even');
                        $('td:first-child', row).html(label + ":&nbsp;");
                        $('td:last-child', row).html(value);
                        table.append(row);
                    }
                }
            };
            $.getJSON(PLATE_WELLS_URL_999.replace('999', tmp.wellId) +
                '?query=Well-' + tmp.wellId +
                '&callback=?',
                onAnnotations);
            $.getJSON(PLATE_LINKS_URL_999.replace('999', tmp.wellId) +
                '?query=Well-' + tmp.wellId +
                '&callback=?',
                onAnnotations);
        }

        // TODO: this used anywhere?
        // {% block xtra_metadata %}{% endblock %}

        /*$('#wblitz-shortname').attr('title', tmp.imageName).html(gs_text_trim(tmp.imageName, 15, true));*/

        tmp = viewport.getSizes();
        $('#wblitz-image-width').html(tmp.width);
        $('#wblitz-image-height').html(tmp.height);
        $('#wblitz-image-z-count').html(tmp.z);
        $('#wblitz-image-t-count').html(tmp.t);
        tmp = viewport.getPixelSizes();
        $('#wblitz-image-pixel-size-x').html(tmp.x==0?'-':(tmp.x.lengthformat()));
        $('#wblitz-image-pixel-size-y').html(tmp.y==0?'-':(tmp.y.lengthformat()));
        $('#wblitz-image-pixel-size-z').html(tmp.z==0?'-':(tmp.z.lengthformat()));

        /* Fill in the Rendering Details box */

        $(".picker").unbind('prepared').unbind('showing').unbind('hiding');
        $('#rdef-postit ul').not('ul:last-child').remove();

        var template = ''
        + '<tr class="$cls rdef-window">'
        + '<td><input id="rd-wblitz-ch$idx0" class="rd-wblitz-ch" type="checkbox" onchange="rdChanSelHelper(this)" $act></td>'
        + '<td colspan="5"><table><tr id="wblitz-ch$idx0-cw" class="rangewidget"></tr></table></td>'
        + '<td><button id="wblitz-ch$idx0-color" class="picker squarred">&nbsp;</button></td>'
        + '</tr>';

        tmp = $('#rdef-postit table tr:first');
        tmp.siblings().remove();
        for (i=channels.length-1; i>=0; i--) {
            tmp.after(template
                .replace(/\$act/g, channels[i].active?'checked':'')
                .replace(/\$idx0/g, i) // Channel Index, 0 based
                .replace(/\$idx1/g, i+1) // Channel Index, 1 based
                .replace(/\$cwl/g, channels[i].label) // Wavelength
                .replace(/\$cls/g, i/2!=parseInt(i/2)?'even':'odd') // class
            );
            $('#wblitz-ch'+(i)+'-cw').rangewidget({
                min: channels[i].window.min,
                max: channels[i].window.max,
                template: '<td width="10%"><span class="min" title="min: $min">$start</span></td><td><div class="rangeslider" id="wblitz-ch'+i+'-cwslider"></div></td> <td width="10%"><span class="max" title="max: $max">$end</span></td>',
                lblStart: '',
                lblEnd: ''});
            $('#wblitz-ch'+i+'-cwslider').slider({
                range: true,
                min: Math.min(channels[i].window.min, channels[i].window.start+1),  // range may extend outside min/max pixel
                max: Math.max(channels[i].window.max, channels[i].window.end-1),
                values: [ channels[i].window.start+1, channels[i].window.end-1 ],
                slide: function(event, ui) {
                    $('#wblitz-ch'+$(event.target).data('channel-idx')+'-cw-start').val(ui.values[0]).change();
                    $('#wblitz-ch'+$(event.target).data('channel-idx')+'-cw-end').val(ui.values[1]).change();
                },
                stop: function(event, ui) {
                    applyRDCW(viewport);
                }
                }).data('channel-idx', i);
            cb = function (i) {
                return function (e) {
                    var new_start = e.target.value,
                    $sl = $('#wblitz-ch'+i+'-cwslider'),
                    end = $sl.slider('values')[1]
                    min = $sl.slider( "option", "min" );
                    $sl.slider('values', 0, Math.min(new_start, end));    // ensure start < end
                    $sl.slider( "option", "min", Math.min(min, new_start) );   // extend range if needed
                    show_change($('#wblitz-ch'+i+'-cw-start').get(0), channels[i].window.start, 'changed');
                };
            };
            $('#wblitz-ch'+i+'-cw-start').val(channels[i].window.start).unbind('change').bind('change', cb(i));
            $('#wblitz-ch'+i+'-cw-start').keyup(function(event){
                if (event.keyCode === 13){
                    applyRDCW(viewport);
                }
            });
            cb = function (i) {
                return function (e) {
                    var new_end = e.target.value,
                    $sl = $('#wblitz-ch'+i+'-cwslider'),
                    start = $sl.slider('values')[0]
                    max = $sl.slider( "option", "max" );
                    $sl.slider('values', 1, Math.max(new_end, start));    // ensure end > start
                    $sl.slider( "option", "max", Math.max(max, new_end) );   // extend range if needed
                    show_change($('#wblitz-ch'+i+'-cw-end').get(0), channels[i].window.end, 'changed');
                };
            };
            $('#wblitz-ch'+i+'-cw-end').val(channels[i].window.end).unbind('change').bind('change', cb(i));
            $('#wblitz-ch'+i+'-cw-end').keyup(function(event){
                if (event.keyCode === 13){
                    applyRDCW(viewport);
                }
            });
        };


        /* Prepare color picker buttons */
        $(".picker")
            .colorbtn()
            .bind('showing', function () {
                var t = $(this).parents('.postit');
                if (t.length) {
                  var offset = t.offset();
                  offset.left += t.width();
                } else {
                  var offset = {'top':'200px', 'right': '300px'};
                }
                $('#cbpicker-box').css(offset);
                $('.picker-selected').html('&nbsp;');
                $(this).parent().siblings('.picker-selected').html('&gt;');
            })
            .bind('hiding', function () {$(this).parent().siblings('.picker-selected').html('&nbsp;')})
            .bind('prepared', function () {
                zindex_automator('.postit', 210, $('#cbpicker-box'));
            })
            .bind('changed', function () {
                applyRDCW(viewport);
            });

        // Don't see any obvious bugs when these are removed.
        // They are both bound to appropriate triggers on viewport.
        //projectionChange(null,null, true);
        //modelChange();

        syncRDCW(viewport);

        $('#wblitz-workarea > .box > div.row').show();
    };

}());