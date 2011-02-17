$(function() {
    loadCalendar();

});

loadCalendar = function(){
    $.post(basePath + 'schedule/calendar/', {}, function(calendar_data){
        createCalendarNew(calendar_data);    
    }, 'json');
};

createCalendarNew = function(c_data)
{
    var calendar_hours = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
    var calendar_days = ['Su','Mo','Tu','We','Th','Fr','Sa'];
    var calendar_minutes = [0,5,10,15,20,25,30,35,40,45,50,55];


    conflicts = String(c_data.conflicts.conflicting_sections);
    calendar_data = c_data.meetings;

    $('div[id^="min-div"]').removeClass('busy').removeClass('busy-with-conflict').attr('title','');
    for (var i=0; i < calendar_data.length; i++){
        var weekdays = [];
        days = calendar_data[i].weekdays;
        start_hour = calendar_data[i].start_hour;
        start_minute = calendar_data[i].start_minute;
        end_hour = calendar_data[i].end_hour;
        end_minute = calendar_data[i].end_minute;
        section = calendar_data[i].section;
        start_date = new Date(calendar_data[i].start_date);
        end_date = new Date(calendar_data[i].end_date);

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

        temp_hour = start_hour;
        temp_minute = start_minute;
        
        while (temp_hour <= end_hour){
            while ((temp_hour<end_hour && (temp_minute <= end_minute || temp_minute<=55)) || (temp_hour == end_hour && temp_minute <= end_minute)){
                for (var j=0; j<weekdays.length; j++){
                    class_to_add = 'busy';
                    if ($('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).attr('title')){
                        current_title = $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).attr('title');
                        if (current_title.indexOf(section) == -1){
                            new_title = current_title + ', ' + section;
                            $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).removeClass('busy').removeClass('busy-with-conflict');
                            if (conflicts.indexOf(section) != -1){
                                temp_array = new_title.split(",");
                                for (var k=0; k<temp_array.length; k++){
                                    if (temp_array[k] != section){
                                        for (var n=0; n<calendar_data.length; n++){
                                            temp_start_date = new Date(calendar_data[n].start_date);
                                            temp_end_date = new Date(calendar_data[n].end_date);
                                            if ((start_date >= temp_start_date && start_date <= temp_end_date) || (end_date >= temp_start_date && end_date <= temp_end_date)){
                                                class_to_add = 'busy-with-conflict';
                                            }

                                        }
                                    }
                                }
                            }
                        }
                        else{
                            new_title = current_title;
                        }
                    }
                    else{
                        new_title = section;
                    }
       
                    $('#min-div-'+weekdays[j]+'-'+temp_hour+'-'+temp_minute).addClass(class_to_add).attr('title',new_title);
                    if (temp_minute == '0'){
                        $('#min-div-'+weekdays[j]+'-'+temp_hour+'-0').parent().attr('title', new_title);
                    }
                }
                temp_minute = temp_minute + 5;
            }
            temp_hour = temp_hour +1;
            temp_minute = 0;
        }
    }
};

createCalendar = function(calendar_data)
{
    var calendar_hours = [6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22];
    var calendar_days = [0,1,2,3,4,5,6];
    var calendar_minutes = [0,5,10,15,20,25,30,35,40,45,50,55];
    var calendar_html = '<tr><td>';

    for (var i=0; i<calendar_hours.length; i++){
        if (calendar_hours[i]%2 == 0){
            cal_hours = '' + calendar_hours[i];
            if (calendar_hours[i]-12 > 0){
                cal_hours = calendar_hours[i] - 12 + ' pm';           
            }
            else if (calendar_hours[i]-12 == 0){
                cal_hours = calendar_hours[i] + ' pm';
            }
            else{
                cal_hours = cal_hours + ' am';
            }
        }    
        else {
            cal_hours = '';
        }
            
        calendar_html = calendar_html + '<div id="hour-div">' + cal_hours;
        for (var j=0; j<calendar_minutes.length; j++){
            calendar_html = calendar_html + '<div id="min-div"></div>';
        }
        calendar_html = calendar_html + '</div>';
    }

    for (var i=0; i < calendar_days.length; i++){
        switch(i){
            case 0:
                my_day='Su';
                break;
            case 1:
                my_day='Mo';
                break;
            case 2:
                my_day='Tu';
                break;
            case 3:
                my_day='We';
                break;
            case 4:
                my_day='Th';
                break;
            case 5:
                my_day='Fr';
                break;
            case 6:
                my_day='Sa';
                break;
        }
        calendar_html = calendar_html + '<td>';
        
        for (var j=0; j < calendar_hours.length; j++){
            calendar_html = calendar_html + '<div id="weekday-hour-div">&nbsp;';
            for (var k=0; k < calendar_minutes.length; k++){
                calendar_html = calendar_html + '<div id="min-div-' + my_day + '-' + calendar_hours[j] + '-' + calendar_minutes[k] + '" class="min-div"></div>';
              
            }

            calendar_html = calendar_html + '</div>';
        }
        
        calendar_html = calendar_html + '</td>';
    }
        
    calendar_html = calendar_html + '</tr>';
    $('.calendar-table tbody').empty();
    $('.calendar-table tbody').append(calendar_html);

    for (var i=0; i < calendar_data.length; i++){
        day = calendar_data[i].day;
        hour = calendar_data[i].hour;
        minute = calendar_data[i].minute;
        section = calendar_data[i].section;
        new_title = '';
        class_to_add = 'busy';
        if ($('#min-div-'+day+'-'+hour+'-'+minute).attr('title')){
            current_title = $('#min-div-'+day+'-'+hour+'-'+minute).attr('title');
            if (current_title.indexOf(section) == -1){
                new_title = current_title + ', ' + section;
                class_to_add = 'busy-with-conflict';
            }
            else{
                new_title = current_title;
            }
        }
        else{
            new_title = section;
        }
        
        $('#min-div-'+day+'-'+hour+'-'+minute).addClass(class_to_add).attr('title',new_title);
        if (minute == '0'){
            $('#min-div-'+day+'-'+hour+'-0').parent().attr('title', new_title);
        }
    }

};
