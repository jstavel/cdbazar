$("a.paginate").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.pagination').html(data['paginator.html']); 
			$('.tradeaction_list .list').html(data['eshop/tradeaction_list/list.html']); 
			eval(data['eshop/tradeaction_list/js.js']);
		},
	});
	return false;
});
