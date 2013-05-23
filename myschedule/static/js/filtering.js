$(function(){

    setForm(); //set returned values of hidden form to visible form

    // if a selection is made on the visible form it instantly updates the hidden form
    $('#sidebar-search select').change(function(){
        console.log($('#sidebar-search div select').val());
        updateHidden($(this).parent().attr('class'), $(this).val());
    });
    $('#sidebar-search input[type="radio"]').change(function(){
        updatesort($(this).parent().attr('class'));
    });
    $('#sidebar-search input[type="text"]').change(function(){
        updatedates($(this).parent().attr('class'), $(this).val());
    });
    // Change event listener for the hidden form to register a click event for the search when the form changes.
    $('#main-search select').change(function(){
        $('button#course-search').trigger('click');
    });
    $('#main-search input').change(function(){
        $('button#course-search').trigger('click');
    });
    $('a#remove-all-filters').click(function(){
        $('button#course-search').trigger('click');
    });

    $('button#course-search').click(function(){
        $('#loader').show();
        $('#loader-cover').show();
    });

});

function updateHidden(divClass, value, type='select'){
    element = '#main-search fieldset .'+divClass+' '+type;
    console.log(element);
    $(element).val(value).change(); //updates hidden form field value and fires change event.
};

function updatesort(divClass){
    element = '#main-search fieldset .'+divClass+' input[type="radio"]';
    $(element).attr('checked','checked').change(); //updates hidden form field value and fires change event.
};

function updatedates(divClass, value){
    element = '#main-search fieldset .'+divClass+' input[type="text"]';
    $(element).val(value).change(); //updates hidden form field value and fires change event.
};
//function to sync the visible form to the hidden form on load.
function setForm(){
    $('#sidebar-search fieldset .prefix input').attr('checked',$('#main-search fieldset .prefix input').attr('checked'));
    $('#sidebar-search fieldset .title input').attr('checked',$('#main-search fieldset .title input').attr('checked'));
    $('#sidebar-search fieldset .academic_level select').val($('#main-search fieldset .academic_level select').val());
    $('#sidebar-search fieldset .campus select').val($('#main-search fieldset .campus select').val());
    $('#sidebar-search fieldset .delivery_method select').val($('#main-search fieldset .delivery_method select').val());
    $('#sidebar-search fieldset .term select').val($('#main-search fieldset .term select').val());
    $('#sidebar-search fieldset .start_date input').val($('#main-search fieldset .start_date input').val());
    $('#sidebar-search fieldset .end_date input').val($('#main-search fieldset .end_date input').val());
};

