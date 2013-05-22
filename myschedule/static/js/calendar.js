$(function() {
    loadCalendar();
    if(document.LOGGEDIN == false){
        $('#register-button').attr('href', document.LOGIN_URL);
        $('#map-button').attr('href', document.LOGIN_URL);
    }
});

loadCalendar = function(){
    $.post(basePath + 'schedule/calendar/', {}, function(calendar_data){
        createCalendar(calendar_data);    
    }, 'json');
};

createCalendar = function(calendar_data)
{
    // This function cycles through the meeting data passed to it and sets the
    // appropriate class on the time divs to indicate busy times and busy times
    // that are in conflict (due to multiple classes with the same time).
    conflicts = String(calendar_data.conflicts.conflicting_sections);
    meetings = calendar_data.meetings;

    // Hide the sidebar conflict message.
    $('.sidebar-message').hide();
    // Clear out the calendar by removing any classes and title/sections values currently assigned.
    $('div[id^="min-div"]').removeClass('busy').removeClass('busy-with-conflict').attr('title','').attr('sections','');

    for (var i=0; i < meetings.length; i++){
        var weekdays = [];
        days = meetings[i].weekdays;
        start_hour = meetings[i].start_hour;
        start_minute = meetings[i].start_minute;
        end_hour = meetings[i].end_hour;
        end_minute = meetings[i].end_minute;
        section = meetings[i].section;
        start_date = new Date(meetings[i].start_date);
        end_date = new Date(meetings[i].end_date);
        // First determine which days of the week this meeting occurs on
        if (days.indexOf('M')!=-1){
            weekdays.push('Mo');
        }
        if (days.indexOf('T')!=-1){
            weekdays.push('Tu');
        }
        if (days.indexOf('W')!=-1){
            weekdays.push('We');
        }
        if (days.indexOf('R')!=-1){
            weekdays.push('Th');
        }
        if (days.indexOf('F')!=-1){
            weekdays.push('Fr');
        }
        if (days.indexOf('S')!=-1){
            weekdays.push('Sa');
        }
        if (days.indexOf('U')!=-1){
            weekdays.push('Su');
        }
        new_title = '';
        new_sections = '';

        temp_hour = start_hour;
        temp_minute = start_minute;
        
        // For the time range that this class meets, set the busy or busy-with-conflict class
        // on the corresponding minute divs.  Keep in mind these divs represent 5 minute increments
        // of time.
        while (temp_hour <= end_hour){
            while ((temp_hour<end_hour && (temp_minute <= end_minute || temp_minute<=55)) || (temp_hour == end_hour && temp_minute <= end_minute)){
                // Need to set the class on the same time divs for each day the class meets.
                for (var j=0; j<weekdays.length; j++){
                    // default class is busy
                    class_to_add = 'busy';
                    if ($('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).attr('sections')){
                        // If the title and sections attributes have already been set for a time div,
                        // the potential for conflict exists - it will depend upon whether or not the
                        // start and end dates of the classes overlap.
                        current_title = $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).attr('title');
                        current_sections = $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).attr('sections');
                        if (current_sections.indexOf(section) == -1){
                            new_title = current_title + ', ' + section.replace(/-/g,' ').replace('fa','Fall').replace('sp','Spring').replace('su','Summer');
                            new_sections = current_sections + ',' +section;
                            // Remove any previous busy class that was set for this div (it may have been previously
                            // classified as busy and now it might need to be busy-with-conflict.
                            $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).removeClass('busy');
                            // To further determine the possibility of this class having a time conflict with
                            // another, see if it exists in the sections that are in conflict (note: the view
                            // that determines conflicts can only indicate which sections and meeting_ids are 
                            // in conflict - it doesn't check for specific time increments since that is only
                            // a concern for the calendar - hence the reason we check the time increments in
                            // here.
                            if (conflicts.indexOf(section) != -1){
                                // In order to determine which sections this one could potentially be in
                                // a time conflict with, we compare the class start and end dates for this section
                                // against the other sections that were already added to the sections attribute for this
                                // div.
                                temp_sections = new_sections.split(",");
                                for (var k=0; k<temp_sections.length; k++){
                                    // Make sure we don't compare it to itself.
                                    if (temp_sections[k] != section && conflicts.indexOf(temp_sections[k]) != -1){
                                        // Have to find the meeting data for the section we're comparing to
                                        for (var n=0; n<meetings.length; n++){
                                            if (meetings[n].section == temp_sections[k]){
                                                // Compare the dates (note: to work in IE, dates must be
                                                // in the format month/day/year).
                                                temp_start_date = new Date(meetings[n].start_date);
                                                temp_end_date = new Date(meetings[n].end_date);
                                                if ((start_date >= temp_start_date && start_date <= temp_end_date) || (end_date >= temp_start_date && end_date <= temp_end_date) ||
                                                    (temp_start_date >= start_date && temp_start_date <= end_date) || (temp_end_date >= start_date && temp_end_date <= end_date)){
                                                    // This section is in conflict with another.
                                                    class_to_add = 'busy-with-conflict';
                                                    $('.sidebar-message').show();
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        else{
                            // Shouldn't really have this situation - it was mean the section had already been
                            // processed.
                            new_title = current_title;
                            new_sections = current_sections;
                        }
                    }
                    else{
                        // This would be the first (and possibly only) section in this time slot.
                        new_title = section.replace(/-/g,' ').replace('fa','Fall').replace('sp','Spring').replace('su','Summer');
                        new_sections = section;
                    }
                    // Actually apply the class plus title and sections attributes to the time div.
                    // (Don't apply if time is past 10:30 pm - otherwise it will overrun bottom of calendar.)
                    if (parseInt(temp_hour) < 22 || (parseInt(temp_hour) == 22 && parseInt(temp_minute) <= 30)){
                        $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).addClass(class_to_add).attr('title',new_title).attr('sections',new_sections);
                    }
                    if (temp_minute == '0'){
                        // Because of how the divs are laid out, if this happens to be the first
                        // min-div in the weekday-hour-div, also apply the same title to the
                        // weekday-hour-div (works better with cursor movement over the calendar)
                        $('#min-div-'+weekdays[j]+'-'+temp_hour+'-0').parent().attr('title', new_title);
                    }
                }
                // increment time by 5 minutes
                temp_minute = temp_minute + 5;
            }
            // increment to next hour which requires a minute reset back to zero
            temp_hour = temp_hour +1;
            temp_minute = 0;
        }
    }
};
