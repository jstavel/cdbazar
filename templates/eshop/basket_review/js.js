$("a.from-basket").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.review').html(data['eshop/basket_review/review.html']);
			eval(data['eshop/from_basket/js.js']);
			eval(data['eshop/basket/js.js']);
			eval(data['eshop/basket_rewiew/js.js']);
		},
	});
	return false;
});
