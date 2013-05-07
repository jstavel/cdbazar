$("a.paginate").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.pagination').html(data['paginator.html']); 
			$('.article_list .list').html(data['store/article_list/list.html']); 
			eval(data['store/article_list/js.js']);
		},
	});
	return false;
});
$(".article .tools a.edit").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.article_edit .modal-body').html(data['store/article_form/form.html']);
			$('.article_edit').modal();
			eval(data['store/article_form/js.js']);
		},
	});
	return false;
});
$(".article_list .tools a.add").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.article_edit .modal-body').html(data['store/article_form/form.html']);
			$('.article_edit').modal();
			eval(data['store/article_form/js.js']);
		},
	});
	return false;
});
// $(".article .tools").each(function(){
// 	var parent = $(this).closest(".article");
// 	$(this).position({ my: "right bottom", at: "right bottom", of: parent  });
// });
