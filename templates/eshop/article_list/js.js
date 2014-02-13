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
$("a.paginate").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.pagination').html(data['paginator.html']); 
			$('.article_list .list').html(data['eshop/article_list/list.html']); 
			$('.article_list .list-shortly').html(data['eshop/article_list/list_shortly.html']); 
			eval(data['eshop/article_list/js.js']);
		},
	});
	return false;
});
