$("a.from-basket").click(function(){
	var link = $(this);
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.basket-review').hide().html(data['store/basket_review/list.html']).fadeIn();
			eval(data['store/basket_review/js.js']);
		},
	});
	return false;
});
