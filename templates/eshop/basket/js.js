$("a.from-basket").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.basket').html(data['eshop/basket/summary.html']);
			eval(data['eshop/to_basket/js.js']);
			eval(data['eshop/basket/js.js']);
		},
	});
	return false;
});
