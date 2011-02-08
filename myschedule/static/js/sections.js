$(function() {
    $('a.add-item').click(function() {
        section = $(this).attr('ref').replace('section_','');
        $(this).parents('.section').hide();
        addItem(section);
    });

    // Check each section listed - if it has already been added to the cart
    // hide it from view (it will be shown later if the item is deleted from the cart).
    $('a.add-item').each(function(){
        section = $(this).attr('ref').replace('section_','');
        $('a.remove-link').each(function(){
            if (section = $(this).attr('ref')){
                $('#' + section).hide();
            }
        });
    });
});

function addItem(section)
{
    $.post(basePath + 'cart/add/', {section: section}, function(data){
            if (data.errors != ''){
                alert(data.errors);
            }
            else{
                section_data = data.section_data;
                item_html = '<li class="remove-item"><a class="remove-link" href="#remove" ref="' + section + '" ><img src="' + buttonPath + '" alt="Remove"/></a>' + section_data.prefix + ' ' + section_data.course_number + ' - ' + section_data.section_number + '<br/>' + section_data.title +'</li>';
                $('#cart').append(item_html);
                // Re-instantiate click event otherwise the delete won't work for item added to the sidebar.
                $("a.remove-link").click(remove_section);
                loadCalendar();
            }
    }, 'json');
};
