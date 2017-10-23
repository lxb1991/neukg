/**
 * Created by lxbmain on 2017/6/26.
 */

$(function(){

    $(window).scroll(function() {

        if ($(this).scrollTop() != 0) {

            $('#toTop').fadeIn();
        } else {

            $('#toTop').fadeOut();
        }
    });

    $('#toTop').click(function() {

        $('body,html').animate({ scrollTop: 0 }, 800);
    });

});

function query() {

    var query = $('#query_word').val().trim();

    if(query == "") {

        alert('请输入关键字');

    }else{

        var url = "/search/";

        const finalUrl = url + query +'/';

        window.location.href = finalUrl;
    }
}