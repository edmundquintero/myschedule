$(function() {
    // Create modal dialog windows, overriding parameters for a specific
    // dialog in the processing for the click function.
    $('a.open-window').each(function(){
        createModalWindow($(this).attr('ref'), $(this).attr('dialog-title'),
            closeDialog, closeDialog);
    });

    // Override any dialog specific parameters and open appropriate selected
    // window.
    $('a.open-window').click(function(event) {
        if($(this).attr('ref') == 'email') {
            buttons = { "Cancel": closeDialog,
                        "Send": sendEmail }
        }
        if($(this).attr('ref') == 'show-note') {
            buttons = { "Close": closeDialog }
            $('#show-note').empty();
            $('#show-note').append('<p>'+$(this).attr('dialog-note')+'</p>');
        }
        if($(this).attr('ref') == 'book') {
            $('a.booklink').attr('href', $(this).attr('booklink'));
            buttons = { "Close": closeDialog }
            $('#' + $(this).attr('ref')).dialog('option','width',850);
            $('#' + $(this).attr('ref')).dialog('option','minHeight',850);
        }
        $('#' + $(this).attr('ref')).dialog('option','buttons', buttons);
        $('#' + $(this).attr('ref')).dialog('open');
        if($(this).attr('ref') == 'book') {
            // Have to load iframe containing book info after opening dialog
            // (to make IE happy).
            $('.book').empty();
            $('.book').append('<iframe id="book-frame" frameBorder="1" width="99%" height="850" src="' + $(this).attr('booklink') + '"><p>Your browser does not support iframes. Book information can be viewed <a class="booklink" href="' + $(this).attr('booklink') + '">here</a></p></iframe>');
        }
    });

    $("a.print-schedule").click(function() {window.print();});
    $("a.remove-link").click(remove_section);

    sidebar_section_count = $('li.remove-item').length;
    //sidebar_hidden_count = $('li.remove-item:hidden').length;
    if (sidebar_section_count == 0){
        $('#view-full-schedule').hide();
    }

});

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
    $.post(basePath + 'schedule/delete/', {section:$(this).attr('ref')});
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
            $('p[id="login-message"]').each(function(){
                $('#conflict-login-message').show();
            });
        }
    }, 'json');
    loadCalendar();
}
