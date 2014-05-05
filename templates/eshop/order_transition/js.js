$('#id_emailMessageID').change(function (){
        $('#submit-load-emailmessage').attr('type','text');
        jQuery.ajax({
                type: 'POST',
                url: $('#form-transition').attr('action'),
                data: $('#form-transition').serialize(),
                success: function(data){
                        $('.detail').html(data['eshop/order_transition/form.html']);
                        eval(data['eshop/order_transition/js.js']);
                }
        });
});
$('#submit-load-emailmessage').hide();
