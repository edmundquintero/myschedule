$(function(){

    setForm(); //set returned values of hidden form to visible form

    // if a selection is made on the visible form it instantly updates the hidden form
    $('#sidebar-search fieldset div select').change(function(){
        console.log($('#sidebar-search div select').val());
        updateHidden($(this).parent().attr('class'), $(this).val());
    });
    $('#sidebar-search fieldset div input[type="radio"]').change(function(){
        updatesort($(this).parent().attr('class'));
    });
    $('#sidebar-search fieldset div input[type="text"]').change(function(){
        updatedates($(this).parent().attr('class'), $(this).val());
    });
    // Change event listener for the hidden form to register a click event for the search when the form changes.
    $('#main-search fieldset div select').change(function(){
        $('button#course-search').trigger('click');
    });
    $('#main-search fieldset div input').change(function(){
        $('button#course-search').trigger('click');
    });
    $('a#remove-all-filters').click(function(){
        $('button#course-search').trigger('click');
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
    $('#sidebar-search .academic_level select').val($('#main-search .academic_level select').val());
    $('#sidebar-search .academic_level input[type="text"]').val($('#main-search .academic_level input[type="text"]').val());
    $('#sidebar-search .academic_level input[type="radio"]').attr('checked', $('#main-search .academic_level input[type="radio"]').attr('checked'));
};

