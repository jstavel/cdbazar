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
// $(".tradeaction .tools a.edit").click(function(){
// 	$.ajax({
// 		type: 'GET',
// 		url: $(this).attr('href'),
// 		success: function(data){ 
// 			$('.tradeaction_edit .modal-body').html(data['eshop/tradeaction_form/form.html']);
// 			$('.tradeaction_edit').modal();
// 			eval(data['eshop/tradeaction_form/js.js']);
// 		},
// 	});
// 	return false;
// });
// $(".tradeaction_list .tools a.add").click(function(){
// 	$.ajax({
// 		type: 'GET',
// 		url: $(this).attr('href'),
// 		success: function(data){ 
// 			$('.tradeaction_edit .modal-body').html(data['eshop/tradeaction_form/form.html']);
// 			$('.tradeaction_edit').modal().on('shown', function(){
// 			        eval(data['eshop/tradeaction_form/js.js']);
//                                 });
// 		},
// 	});
// 	return false;
// });
