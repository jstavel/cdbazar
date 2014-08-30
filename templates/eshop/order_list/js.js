$("a.paginate").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.pagination').html(data['paginator.html']); 
			$('.order_list .list').html(data['eshop/order_list/list.html']); 
			eval(data['eshop/order_list/js.js']);
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
                        $('#form-transition .form').html(data['eshop/order_list/form.html']);
                        eval(data['eshop/order_list/js.js']);
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
$('input[name="all"]').change(function(){
        var checkedAll = $(this)[0].checked;
        console.log('checked: ' + checkedAll);
        $('input.order-id-checkbox').each(function(){
                $(this)[0].checked = checkedAll;
        });
})
