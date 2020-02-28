/*jslint browser:true */
/*globals onUpdate*/

function normalizeIP(ip_address) {
    'use strict';
    return ip_address ? ip_address.split(':').join('').split('.').join('') : null;
}

function dismissAddAnotherPopup(win, ip_address) {
    'use strict';
    win.close();
    var id = normalizeIP(ip_address);
    var host = django.jQuery('#addr_' + id);
    host.replaceWith('<a class="used" id="addr_' + id + '">' + ip_address + '</a>');
}

django.jQuery(function ($) {
    'use strict';
    $('#jstree').on('ready.jstree', function (e, data) {
        // A trick to open the tree automatically
        // till the point of the current node only.
        $('#jstree').jstree(true).select_node(window.current_subnet);
        $('#jstree').jstree(true).deselect_node(window.current_subnet);
    });
    $('#jstree').jstree().bind('activate_node.jstree', function (e, data) {
        // Open the specific subnet page that used clicked on.
        document.location.href = data.node.a_attr.href;
    });
});


function initHostsInfiniteScroll($, current_subnet, address_add_url, address_change_url, ip_uuid) {
    'use strict';
    var renderedPages = 5,
        fetchedPages = [],
        busy = false,
        nextPageUrl = '/api/v1/subnet/' + current_subnet + '/hosts',
        lastRenderedPage = 0; //1 based indexing (0 -> no page rendered)
    function addressListItem(addr) {
        var id = normalizeIP(addr.address);
        if (addr.used) {
            var uuid = ip_uuid[addr.address];
            //note 1234 was passed as a dummy to be later on replaced in the script
            return '<a class = "used" href=\"' + address_change_url.replace('1234', uuid) +
                '?_to_field=id&amp;_popup=1&amp;ip_address=' + addr.address +
                '&amp;subnet=' + current_subnet + '"onclick="return showAddAnotherPopup(this);">' +
                addr.address + '</a>';
        }
        return '<a href=\"' + address_add_url + '?_to_field=id&amp;_popup=1&amp;ip_address=' +
            addr.address + '&amp;subnet=' + current_subnet + '"onclick="return showAddAnotherPopup(this);" ' +
            'id="addr_' + id + '">' +
            addr.address + '</a>';
    }
    function pageContainer(page) {
        var div = $('<div class="page"></div>');
        page.forEach(function (address) {
            div.append(addressListItem(address));
        });
        return div;
    }
    function appendPage() {
        $('.subnet-visual').append(pageContainer(fetchedPages[lastRenderedPage]));
        if (lastRenderedPage >= renderedPages) {
            var removedDiv = $('.subnet-visual div:first');
            $('.subnet-visual').scrollTop($('.subnet-visual').scrollTop() - removedDiv.height());
            removedDiv.remove();
        }
        lastRenderedPage += 1;
        busy = false;
        onUpdate();
    }
    function fetchNextPage() {
        $.ajax({
            type: 'GET',
            url: nextPageUrl,
            success: function (res) {
                fetchedPages.push(res.results);
                nextPageUrl = res.next;
                appendPage();
            },
            error: function (error) {
                busy = false;
                throw error;
            },
        });
    }
    function pageDown() {
        busy = true;
        if (fetchedPages.length > lastRenderedPage) {
            appendPage();
        } else if (nextPageUrl !== null) {
            fetchNextPage();
        } else {
            busy = false;
        }
    }
    function pageUp() {
        busy = true;
        if (lastRenderedPage > renderedPages) {
            $('.subnet-visual div:last').remove();
            var addedDiv = pageContainer(fetchedPages[lastRenderedPage - renderedPages - 1]);
            $('.subnet-visual').prepend(addedDiv);
            $('.subnet-visual').scrollTop($('.subnet-visual').scrollTop() + addedDiv.height());
            lastRenderedPage -= 1;
        }
        busy = false;
    }
    function onUpdate() {
        if (!busy) {
            var scrollTop = $('.subnet-visual').scrollTop(),
                scrollBottom = scrollTop + $('.subnet-visual').innerHeight(),
                height = $('.subnet-visual')[0].scrollHeight;
            if (height * 0.75 <= scrollBottom) {
                pageDown();
            } else if (height * 0.25 >= scrollTop) {
                pageUp();
            }
        }
    }
    $('.subnet-visual').scroll(onUpdate);
    onUpdate();
}
