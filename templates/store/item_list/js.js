$("a.paginate").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.pagination').html(data['paginator.html']);
			$('.item_list .list').html(data['store/item_list/list.html']); 
			eval(data['store/item_list/js.js']);
		},
	});
	return false;
});

$("a.edit").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.item_edit .modal-header').html(data['store/item_form/form_header.html']);
			$('.item_edit .modal-body').html(data['store/item_form/form_body.html']);
			$('.item_edit').modal();
		},
	});
	return false;
});

$("a.to-basket").click(function(){
	var from_item = $(this);
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.basket').hide().html(data['store/basket/summary.html']).fadeIn();
			eval(data['store/to_basket/js.js']);
			eval(data['store/basket/js.js']);
			$('.basket-review').hide().html(data['store/basket_review/list.html']).fadeIn();
			eval(data['store/basket_review/js.js']);
			$(from_item).closest('tr.item-detail').fadeOut();
		},
	});
	return false;
});
$('td.field').click(function(){
        var from_item = $(this);
        var itemid = function(item){
                var itemid = $(item).attr('id').split('_').pop();
                return itemid;
        }($(this).closest('tr.item-detail'));
        var field = $(this).attr('my:field');
        var url = ["/store/item",itemid,'edit',field].join('/');
        $.ajax({
                type:'GET',
                url: url,
                success: function(data){
                        $(from_item).unbind('click');
                        $(from_item).html(data['store/item_field_update/form-body.html']);
                        eval(data['store/item_field_update/js.js']);
                },
        });
});
