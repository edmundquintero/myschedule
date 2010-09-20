$(function() {
    // Create modal dialog windows, overriding parameters for a specific
    // dialog in the processing for the click function.
    $('a.open-window').each(function(){
        createModalWindow($(this).attr('ref'), $(this).attr('dialog-title'),
            'auto', closeDialog, closeDialog);
    });

    // Override any dialog specific parameters and open appropriate selected
    // window.
    $('a.open-window').click(function() {
        if($(this).attr('ref') == 'email') {
            buttons = { "Cancel": closeDialog,
                        "Send": sendEmail }
        }
        if($(this).attr('ref') == 'save') {
            buttons = { "Cancel": closeDialog,
                        "Save schedule": saveSchedule }
        }
        $('#' + $(this).attr('ref')).dialog('option','buttons', buttons);
        $('#' + $(this).attr('ref')).dialog('open');
    });

});

function createModalWindow(element, title, height, createCallback,
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
        height: height,
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
    var emails = $('#id_email').val().replace(/ /g,''); // removes spaces
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
        // Submit ajax request to send email.
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

// Process save schedule button on save dialog.
saveSchedule = function()
{
    save_name = $('#id_save_name').val();
    alert(name);
    // Check to see if the schedule name already exists.
    // Save schedule.
    $.post(basePath + 'cart/save/', {description: save_name}, function(messages){
            if (messages.errors != ''){
                alert(messages.errors);
            }
          }, 'json');
    // Close dialog.
    $(this).dialog('close');
};
