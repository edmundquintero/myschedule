$(function(){

    $('.course .course-content').click(function(){
        if (!($(this).hasClass('disable-course'))){
            var link = $(this).attr('ref');
            window.location = link;
        }
    });

});
