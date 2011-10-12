$(function() {
    // Create modal dialog windows, overriding parameters for a specific
    // dialog in the processing for the click function.
    $('a.open-window').each(function(){
        createModalWindow($(this).attr('ref'), $(this).attr('dialog-title'),
            closeDialog, closeDialog);
    });

    createModalWindow('register-status', 'Status', closeDialog, closeDialog);

    // Override any dialog specific parameters and open appropriate selected
    // window.
    $('a.open-window').click(function(event) {
        if($(this).attr('ref') == 'email') {
            buttons = { "Cancel": closeDialog,
                        "Send": sendEmail }
        }

        if($(this).attr('ref') == 'feedback') {
            buttons = { "Close": closeDialog }
            $('#' + $(this).attr('ref')).dialog('option','width',600);
        }

        if($(this).attr('ref') == 'register') {
            buttons = { "Cancel": closeDialog,
                        "Continue": beginRegistration }
        }

        $('#' + $(this).attr('ref')).dialog('option','buttons', buttons);
        $('#' + $(this).attr('ref')).dialog('open');

    });

    $("a.print-schedule").click(function() {window.print();});
    $("a.remove-link").click(remove_section);

    sidebar_section_count = $('li.remove-item').length;
    if (sidebar_section_count == 0){
        $('#view-full-schedule').hide();
    }

    // Clear out query input field when it receives focus.
    $('#id_query').focus(function(){
        $(this).val('').html('');
    });

    // Initially hide advanced search filter options.
    $("#search-filter").hide();

    // Process click function on advanced search link.
    $("a.advanced-search").click(function() {
        $(this).hide('fast');
        $('#search-filter').show('fast','linear');
    });
    $("a.advanced-search-message").click(function() {
        $('#search-filter').show('fast','linear');
    });
    

    // Process click function on remove filter link.
    $("a.remove-filter").click(function() {
        $('#id_term option[value="all"]').attr('selected','selected');
        $('#id_campus option[value="all"]').attr('selected','selected');
        $('#id_delivery_method option[value="all"]').attr('selected','selected');
        $('#id_start_date').val('');
        $('#id_end_date').val('');
        $('input[name="sort_order"]:checked').removeAttr('checked');
        $('input[name="all_courses"]:checked').removeAttr('checked').val('');
        $('#search-filter').hide('fast','linear', function() {
            $('a.advanced-search').show('fast');   
        });
    });

    // Process change on term filter.
    $("#id_term").keyup(updateTerm)
                 .click(updateTerm);
    //Process search button.
    $('#search').submit(processSubmit);

});


function processSubmit()
{
    // If user didn't specify a search query, clear out help text
    // and set it to empty string so all courses will be returned
    if ($('#id_query').val() == 'ex. math, bus 121, mec'){
        $('#id_query').val('');
    }
    // Likewise, if show all courses checkbox is checked, clear
    // out any value in the query so it will return all courses
    if ($('#id_all_courses:checked').val() == 'on'){
        $('#id_query').val('');
    }
    // If no query specified but user did not set show all
    // courses checkbox, set it to checked for them (so
    // it will appear checked on subsequent pages
    if ($('#id_query').val() == ''){
        $('#id_all_courses').attr('checked',true).val('on');
    }
};

updateTerm = function(){
    if ($(this).val() == 'all'){
        $('#id_start_date').val('');
        $('#id_end_date').val('');
    }
    else {
        // retrieve start and end dates for this term
        // and set start and end date filters accordingly
        $.post(basePath + 'schedule/terms/', {term: $(this).val()}, function(term_dates){
            $('#id_start_date').val(term_dates.start_date);
            $('#id_end_date').val(term_dates.end_date);
        }, 'json');
    } 
};

function createModalWindow(element, title, createCallback,
                               cancelCallback)
{
    // Buttons will display in dialog window in reverse to the order in
    // which they are specified below.
    $("#" + element).dialog({
        draggable: false,
        resizable: false,
        title: title,
        bgiframe: true,
        autoOpen: false,
        width: 400,
        height: 'auto',
        modal: true,
        buttons: { Cancel: cancelCallback, Create: createCallback }
    });
};

// Process cancel button on dialog.
closeDialog = function()
{
    $(this).dialog('close');
};

// Process send button on email dialog.
sendEmail = function()
{
    // Separate email addresses and validate they are properly formatted.
    // Separate on commas, spaces, and carriage returns or line feeds.
    var emails = $('#id_email').val().replace(/ /g,',').replace(/\r\n/g,',').replace(/\n/g,',');
    var email_list = emails.split(',');
    var invalid_emails = '';
    var valid_emails = '';
    var email_pattern = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}$/i;
    for (var i=0; i < email_list.length; i++){
        var test_email = email_list[i];
        if (test_email != '' && !(email_pattern.test(test_email))) {
            invalid_emails = invalid_emails + '\n' + test_email;
        }
        else {
            if (test_email != '') {
                valid_emails = valid_emails + ',' + test_email;
            }
        }
    }
    if (invalid_emails == '' && valid_emails != '') {
        // Submit request to send email.
        $.post(basePath + 'schedule/email/', {email_addresses: valid_emails}, function(messages){
            if (messages.errors != ''){
                alert(messages.errors);
            }
        }, 'json');
       
        // Close dialog.
        $(this).dialog('close');
    }
    else {
        if (invalid_emails != '') {
            alert('There is a problem with the following email address(es):' + invalid_emails);
        }
        else {
            alert('You must enter at least one email address or cancel this request.')
        }
    }
};

// Process remove link (in sidebar or from view full schedule).
remove_section = function()
{
    // Remove item from sidebar and redisplay add link in section results
    // (only applies if user deleted section via sidebar).
    $(this).parent('li.remove-item').hide();
    section_code = $(this).attr('ref');
    $('a.add-item[ref="section_'+section_code+'"]').show();
    // If all sections were removed from sidebar, hide view-full-schedule button.
    sidebar_section_count = $('li.remove-item').length;
    sidebar_hidden_count = $('li.remove-item:hidden').length;
    if (sidebar_section_count == sidebar_hidden_count){
        $('#view-full-schedule').hide();
    }
    // Hide section from displaying in schedule (only applies if section deleted
    // on view full schedule page.
    $(this).parents('.section').hide();
    // Actually remove section from session variable, user's saved schedule
    // and recheck conflicts.
    $.post(basePath + 'schedule/delete/', {section:$(this).attr('ref')}, function(message){
        // Note: since the delete process updates the session variable, we don't want it
        // to recheck conflicts and reload the calendar until after the delete process ends.
        // Hence the reason for placing those calls in here.
        $.post(basePath + 'schedule/conflicts/', {}, function(conflicts){
            $('.section-meeting tr').removeClass('error');
            if (conflicts.conflicts.conflicting_meetings.length > 0){
                for (var i=0; i<conflicts.conflicts.conflicting_meetings.length; i++){
                    $('#'+conflicts.conflicts.conflicting_meetings[i]).addClass('error');
                }
            }
            else{
                $('#conflict-message').hide();
                $('#conflict-login-message').hide();
                $('p[id="login-message"],p[id="feedback-message"],p[id="downtime-message"]').each(function(){
                    $('#conflict-login-message').show();
                });
            }
        }, 'json');
        loadCalendar();
    }, 'json');
}

beginRegistration = function(){
    // Call the register view to submit the user's schedule to datatel colleague.
    $(".ui-button :contains('Continue')").addClass("ui-state-disabled").attr('disabled','disabled');

    $.post(basePath + 'schedule/register/', {}, function(messages){
        if (messages.status == 'error' && messages.errors != ''){
            message = 'The following message was received when your schedule was submitted to MyCollege: <br /><em> ' + messages.errors + '</em><br /><br />Please contact the <a href="mailto:helpdesk@cpcc.edu">ITS Help Desk</a> if you need assistance with this error.';
            buttons = { "Cancel": closeDialog}
        }
        else {
            if (messages.status =='ok'){
                message = s2w_success_message;
                buttons = { "Cancel": closeDialog,
                            "Continue": loadColleague }
            }
            else{
                message = 'An unidentified error occurred while attempting to submit your schedule to MyCollege. Please contact the <a href="mailto:helpdesk@cpcc.edu">ITS Help Desk</a> for assistance.';
                buttons = { "Cancel": closeDialog}
            }
        }
        // Close register dialog (and re-enable it's continue button).
        $(".ui-button :contains('Continue')").removeClass('ui-state-disabled').removeAttr('disabled');
        $('#register').dialog('close');
        // Open the register-status dialog.
        $('#register-message').html(message);
        $('#register-status').dialog('option','buttons', buttons);
        $('#register-status').dialog('open');
    }, 'json');

};

loadColleague = function(){
    // Close the register-status dialog and open datatel colleague
    // in another window.
    $('#register-status').dialog('close');
    window.open(s2w_datatel_url);
};
