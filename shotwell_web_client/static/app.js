var _start = 0;
var _query = 0;
var _jg_params = {
    margins: 10,
    border: 10,
    imagesAnimationDuration: 0
};

function loadItems() {
    _start = $('#gallery a').length;
    $.getJSON('/items/?start=' + _start + '&query=' + _query, function(data) {
        $.each(data, function(i) {
            if (data[i].type == 'video')
                v = '?swipeboxvideo=1';
            else
                v = '';
            $('#gallery').append('<a href="/' + data[i].type + '/' + data[i].item_id + v + '"><img src="/thumb/' + data[i].type + '/' + data[i].item_id + '" /></a>');
        });
        $('#gallery').justifiedGallery('norewind', _jg_params);
    });
}

$('.month-list,.day-list').hide();

$('.toggle-year,.toggle-month').click(function(e) {
    e.preventDefault();
    if ($(this).data('clicked')) {
        $(this).data('clicked', 0);
        $(this).html('&#9654;');
        $(this).parent().find('>ul').slideUp();
    } else {
        $(this).data('clicked', 1);
        $(this).html('&#9660;');
        $(this).parent().find('>ul').slideDown();
    }
});

$('.sidebar-nav a.link').click(function(e) {
    e.preventDefault();
    _query = $(this).attr('href').replace(/#/, '');
    $('#gallery').empty();
    $('#gallery').justifiedGallery(_jg_params);
    loadItems();
});

$("#menu-toggle").click(function(e) {
    e.preventDefault();
    if ($('#wrapper').hasClass('toggled'))
        $(this).html('&#9654;');
    else
        $(this).html('&#9664;');
    $("#wrapper").toggleClass("toggled");
});

$('#gallery').justifiedGallery(_jg_params).on('jg.complete', function(){
    $('#gallery a').swipebox();
    window.setTimeout(function() {
        if ($('#gallery').height() < $(window).height())
            loadItems();
    }, 500);
});

$(window).scroll(function() {
    if ($(window).scrollTop() + $(window).height() >= $(document).height()) {
        loadItems();
    }
});

loadItems();
