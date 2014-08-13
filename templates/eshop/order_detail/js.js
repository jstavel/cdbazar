$("a.paginate").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.pagination').html(data['paginator.html']); 
			eval(data['eshop/order_detail/js.js']);
		},
	});
	return false;
});
$('#id_transition').change(function(){
        $('#div_id_emailMessageID').fadeIn();
        $('#div_id_subject').fadeIn();
        $('#div_id_message').fadeIn();
        $('.form-actions').fadeIn();
});
$('#id_emailMessageID').change(function (){
        $('#submit-load-emailmessage').attr('type','text');
        jQuery.ajax({
                type: 'POST',
                url: $('#form-transition').attr('action'),
                data: $('#form-transition').serialize(),
                success: function(data){
                        $('#form-transition').html(data['eshop/order_detail/form.html']);
                        eval(data['eshop/order_detail/js.js']);
                }
        });
});
if( $('#id_transition')[0].value == '0'){
        $('#div_id_emailMessageID').hide();
        $('#div_id_subject').hide();
        $('#div_id_message').hide();
        $('.form-actions').hide();
};
$('#submit-load-emailmessage').hide();
