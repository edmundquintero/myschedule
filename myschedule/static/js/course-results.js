$(function(){

    $('.course .course-content').click(function(){
        var link = $(this).attr('ref');
        window.location = link;
    });

});
