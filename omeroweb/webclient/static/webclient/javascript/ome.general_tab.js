//   Copyright (C) 2016 University of Dundee & Open Microscopy Environment.
//   All rights reserved.

//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU Affero General Public License as
//   published by the Free Software Foundation, either version 3 of the
//   License, or (at your option) any later version.

//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU Affero General Public License for more details.

//   You should have received a copy of the GNU Affero General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.


var TagPane = function TagPane($element, objects) {

    var $header = $element.children('h1'),
        $body = $element.children('div'),
        $tags_container = $("#tags_container");

    var tmplText = $('#tag_template').html();
    var tagTmpl = _.template(tmplText);


    var initEvents = function initEvents() {

        $header.click(function(){
            $header.toggleClass('closed');
            $body.slideToggle();

            var expanded = !$header.hasClass('closed');
            setExpanded(expanded);

            render();
        });

        // Handle events on objects we will load later...
        // $element.on( "click", "tr", function() {
        //     console.log( $( this ).text() );
        // });
    };


    var render = function render() {

        console.log('render', $tags_container.is(":visible"), $tags_container.is(":empty"));

        if ($tags_container.is(":visible") && $tags_container.is(":empty")) {

            $tags_container.html("Loading tags...");

            var request = objects.map(function(o){
                return o.replace("-", "=");
            });
            console.log(request);

            $.getJSON("/webclient/api/annotations/?type=tag&" + request, function(data){

                // manipulate data...
                // make an object of eid: experimenter
                var experimenters = data.experimenters.reduce(function(prev, exp){
                    prev[exp.id + ""] = exp;
                    return prev;
                }, {});

                // Populate experimenters within tags
                var tags = data.annotations.map(function(tag){
                    tag.owner = experimenters[tag.owner.id];
                    if (tag.link && tag.link.owner) {
                        tag.link.owner = experimenters[tag.link.owner.id];
                    }
                    tag.textValue = _.escape(tag.textValue);
                    return tag;
                });
                console.log(tags);

                var html = tagTmpl({'tags': tags});
                // html = _.escape(html);
                $tags_container.html(html);
            });
            
        }
    };


    // We use the "#metadata_general" element to store this data since
    // it is not reloaded on selection change.
    var setExpanded = function setExpanded(expanded) {
        var open_panes = $("#metadata_general").data('open_panes') || [];
        if (expanded && open_panes.indexOf('tags') === -1) {
            open_panes.push("tags");
        }
        if (!expanded && open_panes.indexOf('tags') > -1) {
            open_panes = open_panes.reduce(function(l, item){
                if (item !== 'tags') l.push(item);
                return l;
            }, []);
        }
        $("#metadata_general").data('open_panes', open_panes);
    };

    var getExpanded = function getExpanded() {
        var open_panes = $("#metadata_general").data('open_panes') || [];
        return open_panes.indexOf('tags') > -1;
    };


    initEvents();

    if (getExpanded()) {
        $header.toggleClass('closed');
        $body.show();
    }

    render();
};
