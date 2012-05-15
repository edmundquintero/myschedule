$(function() {
   // Hide anything you don't want the user to see. Added primarily so
   // I could include the actual section.campus field in the section
   // details for filtering purposes only. (The campus displayed in
   // the section header may not be the actual campus value - i.e. Online).
   $('div.hide-me').hide();

    // Process add section button.
    $('a.add-item').click(function() {
        section = $(this).attr('ref').replace('section_','');
        // hide the add link so user will know they've already added the section.
        $(this).hide();
        $('#view-full-schedule').show();
        addItem(section);
    });

    // Check each section listed - if it has already been added to the cart
    // hide it's add link (it will be shown later if the item is deleted from the schedule).
    $('a.add-item').each(function(){
        section = $(this).attr('ref').replace('section_','');
        $('a.remove-link').each(function(){
            if (section = $(this).attr('ref')){
                $('a.add-item[ref="section_'+section+'"]').hide();
            }
        });
    });

    applyFilters();
});

// Additional processing when user selects an add link.
function addItem(section)
{
    $.post(basePath + 'cart/add/', {section: section}, function(data){
            if (data.errors != ''){
                alert(data.errors);
                $('a.add-item[ref="section_'+section+'"]').show();      
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
                    item_html = '<li class="remove-item"><a class="remove-link" href="#remove" ref="' + section + '" ><img src="' + buttonPath + '" alt="Remove"/></a>' + section_data.prefix + ' ' + section_data.course_number + ' - ' + section_data.section_number + '<br/>' + section_data.title.slice(0,19) +'</li>';
                    $('#cart').append(item_html);
                    // Instantiate click event otherwise the delete won't work for item added to the sidebar.
                    // Make sure to specify the section! Bad things (processes remove-section multiple times)
                    // happen if the section isn't specified.
                    $('a.remove-link[ref="'+section+'"]').click(remove_section);
                }
                // Show the view full schedule button in case it was previously hidden.
                $('#view-full-schedule').show();
                $.post(basePath + 'schedule/conflicts/', {}, function(conflicts){ 
                    if (conflicts.conflicts.conflicting_meetings.length > 0){
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

// Process selected filtering (advanced search) criteria.
function applyFilters(){
    campus_filter = $('#id_campus :selected').val();
    start_date_filter = $('#id_start_date').val().replace(/-/g,'/');
    sdf_date = new Date(start_date_filter);
    end_date_filter = $('#id_end_date').val().replace(/-/g, '/');
    edf_date = new Date(end_date_filter);
    delivery_type_filter = $('#id_delivery_method :selected').val();
    $('div.section').each(function(){
        section_campus = $(this).find('div.section-campus').html();
        section_start_date = $(this).find('span.section-start-date').html();
        ssd_date = new Date(section_start_date);
        section_end_date = $(this).find('span.section-end-date').html();
        sed_date = new Date(section_end_date);
        section_delivery_type = $(this).find('div.section-delivery-type').html();
        if ((section_campus == campus_filter || campus_filter == 'all') &&
            (section_delivery_type == delivery_type_filter || delivery_type_filter == 'all')&&
            ((start_date_filter != '' && section_start_date != '' && ssd_date >= sdf_date) || (start_date_filter == '')) &&
            ((end_date_filter != '' && section_end_date != '' && sed_date <= edf_date) || (end_date_filter == ''))){
            $(this).show();
        }
        else{
            $(this).hide();
        }
    });
};

