$('#id_barcode').focus();
$('span.barcode').each(function(){
	var value = $(this).html();
	var element = $(this);
	$.ajax({
		type: 'GET',
		url: '/store/buyout/lookup/?barcode=' + value,
		success: function(data){ 
			element.closest('p.audio3-info').hide().html(data['store/buyout/lookup.html']).fadeIn();
			eval(data['store/js.js']);
		},
	});
});
$(".form2-message").delay(2000).fadeOut("slow", function () { $(this).remove(); });
