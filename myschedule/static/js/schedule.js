$(function() {
    $('#save').hide();
    
    // Display the appropriate message at the top of the page regarding the
    // "saved" status of this cart.
    $('#schedule-name').hide();
    $('#unsaved-schedule').show();
    checkCartSavedStatus();

    // Create modal dialog windows, overriding parameters for a specific
    // dialog in the processing for the click function.
    $('a.open-window').each(function(){
        createModalWindow($(this).attr('ref'), $(this).attr('dialog-title'),
            closeDialog, closeDialog);
    });

    createModalWindow('save-cart', 'Save current schedule?',
             closeDialog, closeDialog); 
    // Override any dialog specific parameters and open appropriate selected
    // window.
    $('a.open-window').click(function(event) {
        if($(this).attr('ref') == 'email') {
            buttons = { "Cancel": closeDialog,
                        "Send": sendEmail }
        }
        if($(this).attr('ref') == 'save') {
            buttons = { "Cancel": closeDialog,
                        "Save schedule": saveSchedule }
            $('#' + $(this).attr('ref')).dialog('option','height',225);
        }
        if($(this).attr('ref') == 'book') {
            $('a.booklink').attr('href', $(this).attr('booklink'));
            buttons = {}
            event.preventDefault();
            $('#book-frame').attr("src", $(this).attr('booklink'));
            $('#' + $(this).attr('ref')).dialog('option','width',850);
            $('#' + $(this).attr('ref')).dialog('option','minHeight',850);
        }
        $('#' + $(this).attr('ref')).dialog('option','buttons', buttons);
        $('#' + $(this).attr('ref')).dialog('open');
    });

    $('a.open-schedule').click(function() {
        selected_schedule = $(this).attr('sections');
        $.post(basePath + 'cart/get/', {}, function(data){
                var cart_array = new Array();
                var sections = new Array();
                var schedule = new Array();
                cart_sections = data.cart_sections;
                saved_schedules = data.saved_schedules;
                cart_array = cart_sections.split('/');
                cart_qty = cart_array.length - 1; //allow for last item being empty
                saved_qty = saved_schedules.length;
                already_saved = 'False';
                if (cart_sections != ''){            
                    // loop through each saved schedule
                    for (var j=0; j<saved_qty; j++){
                        matches = 0;
                        schedule = saved_schedules[j];
                        sections = schedule.sections;
                        section_count = sections.match(/\//g).length
                        // loop through each section in cart
                        for (var i=0; i<cart_qty; i++){
                            if (sections.match(cart_array[i])){
                                matches++;
                            }
                        }
                        if (matches == cart_qty && matches == section_count){
                            already_saved = 'True';
                            break;
                        }
                    }
                    if (already_saved == 'False'){
                        buttons = { "Don't save": skipSave,
                                    "Save now": saveDialog }
                        $('#save-cart').dialog('option','buttons', buttons);
                        $('#save-cart').dialog('open');                   
                    }
                    else{
                        swapCart();
                    }
                }            
                else{
                    swapCart();
                }
        }, 'json');
    });
});

checkCartSavedStatus = function()
{
    // This function gets called when the schedule page is loaded
    // so it can determine which message regarding the status of
    // the cart to display at the top of the page.  Yep, this code is very
    // similar to the code above for the open-schedule event.  Maybe
    // moving some of this code back into python would eliminate the need
    // for duplication (but then I moved it out of python for some reason
    // that I now no longer recall).
    $.post(basePath + 'cart/get/', {}, function(data){
            var cart_array = new Array();
            var sections = new Array();
            var schedule = new Array();
            cart_sections = data.cart_sections;
            saved_schedules = data.saved_schedules;
            cart_array = cart_sections.split('/');
            cart_qty = cart_array.length - 1; //allow for last item being empty
            saved_qty = saved_schedules.length;
            if (cart_sections != ''){            
                // loop through each saved schedule
                for (var j=0; j<saved_qty; j++){
                    matches = 0;
                    schedule = saved_schedules[j];
                    sections = schedule.sections;
                    section_count = sections.match(/\//g).length
                    // loop through each section in cart
                    for (var i=0; i<cart_qty; i++){
                        if (sections.match(cart_array[i])){
                            matches++;
                        }
                    }
                    if (matches == cart_qty && matches == section_count){
                        if (schedule.description != ''){
                            $('#unsaved-schedule').hide();
                            $('#schedule-name').show();
                            $('.schedule-name').html(schedule.description);
                        }
                        break;
                    }
                }
            }
    }, 'json');
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

skipSave = function()
{
    $(this).dialog('close');
    swapCart();

};

saveDialog = function()
{
    // This processes the save dialog that is displayed when the user tries to
    // navigate to a saved schedule without first saving the one that is in the
    // cart.
    $.post(basePath + 'cart/save/', {save_name: $('#id_save_name').val()}, function(messages){
            if (messages.errors != ''){
                alert(messages.errors);
            }
            else{
                $(this).dialog('close');
                swapCart();
            }
    }, 'json');
};

saveSchedule = function()
{
    // This processes the save dialog that is displayed when the Save Schedule
    // button is selected.
    $.post(basePath + 'cart/save/', {save_name: $('#id_save_schedule_name').val()}, function(messages){
            if (messages.errors != ''){
                alert(messages.errors);
            }
            else{
                $(this).dialog('close');
                window.location.pathname = 'myschedule/show_schedule';
            }
    }, 'json');
};


swapCart = function()
{
    $.post(basePath + 'cart/set/', {new_sections: selected_schedule}, function(messages){
            if (messages.errors != ''){
                alert(messages.errors);
            }
            else{
                window.location.pathname = 'myschedule/show_schedule';
            }
    }, 'json');

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



