function updatePage(){
        var data = {};
        $(".pagestate").serializeArray().map(function(x){data[x.name] = x.value;});
    	$.ajax({
		type: 'POST',
		url: "/store/item/",
                data: data,
		success: function(data){ 
			$('div.item_list .pagination').html(data['paginator.html']); 
			$('div.item_list .list').html(data['store/item_list/list.html']); 
			eval(data['store/item_list/js.js']);
		},
	});
};

$("a.paginate").click(function(){
        var href = $(this).attr('href');
        var pageNumber = pageNumberFromHREF(href);
        /*
          $('#id_action option').removeAttr('selected').filter('[value="page"]').attr('selected',true);
        */
        $('#id_action').attr('value','page');
        $('#id_page').attr('value',pageNumber);
        updatePage();
	return false;
});

$('th.sortable').click(function(){
        var th = $(this);
        var sort_key = th.attr('my:sort_key');
        toggleSortOrder(th);
	$('#id_sort_by').attr('value', sort_key);
	$('#id_sort_order').attr('value', getSortOrder(th));
	updatePage();
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

function getSortedTH(){
        return $('th.sortable').filter(function(index){
                var sort_by = $('#id_sort_by').attr('value');
                return ($(this).attr('my:sort_key') == sort_by);
        });
};
function setSortedIcons(){
        $('th.sortable div.icon').removeClass('sorted').removeClass('desc').removeClass('asc');
        var th = getSortedTH();
        var sort_order = $('#id_sort_order').attr('value');
        $(th).find('div.icon').addClass('sorted').addClass(sort_order);
};

function getSortOrder(th){
        var classAttr = $(th).find('div.icon').attr('class');
        return ((classAttr.indexOf('desc') > -1) ? 'desc': 'asc');
};

function toggleSortOrder(th){
        var div = $(th).find('div.icon');
        var newSortOrder = (getSortOrder(th) == 'desc') ? 'asc': 'desc';
        div.removeClass('desc').removeClass('asc').addClass(newSortOrder);
};

setSortedIcons();
