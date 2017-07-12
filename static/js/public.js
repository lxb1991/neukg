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

    $('#query').click(function () {

        if($('#query_word').val().trim() == "") {

            alert('请输入关键字');

        }else{

            $('#form_query').submit();
        }
    });
});