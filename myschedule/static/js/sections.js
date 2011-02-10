$(function() {
    $('a.add-item').click(function() {
        section = $(this).attr('ref').replace('section_','');
        $(this).parents('.section').hide();
        $('#view-full-schedule').show();
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
                // Create the sidebar button for the section.
                section_data = data.section_data;
                exists = 0;
                $('a.remove-link').each(function(){
                    if ($(this).attr('ref')==section){
                        $(this).parents('.remove-item').show();
                        exists = 1;
                    }
                });
                if (exists == 0){
                    item_html = '<li class="remove-item"><a class="remove-link" href="#remove" ref="' + section + '" ><img src="' + buttonPath + '" alt="Remove"/></a>' + section_data.prefix + ' ' + section_data.course_number + ' - ' + section_data.section_number + '<br/>' + section_data.title +'</li>';
                    $('#cart').append(item_html);
                    // Re-instantiate click event otherwise the delete won't work for item added to the sidebar.
                    $('a.remove-link').click(remove_section);
                }
                // Show the view full schedule button in case it was previously hidden.
                $('#view-full-schedule').show();
                $.post(basePath + 'schedule/conflicts/', {}, function(conflicts){ 
                    if (conflicts.conflicts.conflicting_meetings.length > 0){
                        //for (var i=0; i<conflicts.conflicts.conflicting_meetings.length; i++){
                        //    $('#'+conflicts.conflicts.conflicting_meetings[i]).addClass('error');
                        //}
                        if ($('#conflict-message').length == 0){
                            $('#conflict-login-message').append('<p id="conflict-message">This schedule contains scheduling conflicts.</p>');
                        }
                        $('#conflict-message').show();
                        $('#conflict-login-message').show();
                    }
                    else{
                        $('#conflict-message').hide();
                        $('#conflict-login-message').hide();
                        $('p[id="login-message"]').each(function(){
                            $('#conflict-login-message').show();
                        });
                    }
                }, 'json');

                // Re-load the calendar to show newly added sections.
                loadCalendar();
            }
    }, 'json');
};
