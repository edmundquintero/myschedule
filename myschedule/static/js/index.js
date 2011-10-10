$(function(){
    // If the user didn't specify a start date filter in the
    // advanced search on the home page, default the start
    // date to the current date so the search results returns
    // courses currently open (or about to be open) for registration.
    $('input[name="submit"]').click(function() {
        if ($('#id_start_date').val() == ''){

            var today = new Date();
            var dd = today.getDate();
            if (dd <=9){
                dd = '0' + dd;
            }
            var mm = today.getMonth()+1;//January is 0!
            if (mm <=9){
                mm = '0' + mm;
            }
            var yyyy = today.getFullYear();
            start_date_filter = mm + '/' + dd + '/' + yyyy;
            $('#id_start_date').val(start_date_filter); 
        };
    });

    // Set a sample value for the query input field when on the index page.
    if ($('#id_query').val() == ''){
        $('#id_query').val('ex. math, bus 121, mec');
    }
});


