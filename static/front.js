$( document ).ready(function() {
    $('#stockform input[type=radio]').on('change', function(event) {
        var result = $(this).val();
        $('#stockform').submit();
    });
});