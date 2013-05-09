$(function(){

    $('.show-filtering').click(function(){
        if ($('#sidebar-wrapper').css("right")=='0px')
            $('#sidebar-wrapper').animate({right: '-190px'}, 500);
        else
            $('#sidebar-wrapper').animate({right: '0px'}, 500);
    });

    $('button.toggle-button').click(function(){
        if($(this).hasClass('btn-inverse')){
            $(this).removeClass('btn-inverse');
        }else{
            $(this).addClass('btn-inverse');
        }
    });
});


