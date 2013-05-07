$("a.from-basket").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.basket').html(data['store/basket/summary.html']);
			eval(data['store/to_basket/js.js']);
			eval(data['store/basket/js.js']);
		},
	});
	return false;
});
