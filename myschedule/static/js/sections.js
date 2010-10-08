$(function() {
    $('a.add-item').click(function() {
        section = $(this).attr('ref').replace('section_','');
        addItem(section);
    });

});

function addItem(section)
{
    $.post(basePath + 'cart/add/', {section: section}, function(messages){
            if (messages.errors != ''){
                alert(messages.errors);
            }
            else{
                window.location.reload();
            }
    }, 'json');
};
