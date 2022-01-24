$(document).ready(function(){
    $('#password').prop('disabled', true);

    $('#encrypt').click(function(){
        if($(this).is(':checked'))
        {
            $('#password').prop('disabled', false);
        }
        else
        {
            $('#password').prop('disabled', true);
        }
    });
}); 
