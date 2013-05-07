$("a.to-basket").click(function(){
	var from_item = $(this);
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.basket').hide().html(data['eshop/basket/summary.html']).fadeIn();
			eval(data['eshop/to_basket/js.js']);
			eval(data['eshop/basket/js.js']);
			$(from_item).closest('span.article').fadeOut();
		},
	});
	return false;
});