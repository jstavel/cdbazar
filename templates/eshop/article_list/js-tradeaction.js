function updatePageTradeaction(){
        var data = {};
        $(".pagestate").serializeArray().map(function(x){data[x.name] = x.value;});
	$.ajax({
		type: 'POST',
		url: "/eshop/articles-with-tradeaction/",
                data: data,
		success: function(data){ 
			$('#list-with-tradeaction .pagination').html(data['paginator.html']); 
			$('#list-with-tradeaction .list').html(data['eshop/article_list/list_with_tradeaction.html']); 
			$('#list-with-tradeaction .order-by').html(data['eshop/article_list/order-by.html']);
                        $('.mediatype-list').html(data['eshop/mediatype_choose.html']);
			eval(data['eshop/article_list/js-tradeaction.js']);
		},
	});
};

$('#list-with-tradeaction a[href="#list-by-cheaper"]').click(function(){
        /*
          $('#id_sort option').removeAttr('selected').filter('[value="by-cheaper"]').attr('selected',true);
          $('#id_action option').removeAttr('selected').filter('[value="sort"]').attr('selected',true);
        */
        $('#id_sort').attr('value','by-cheaper');
        $('#id_action').attr('value','sort');
        $('#id_page').attr('value',1);
        updatePageTradeaction();
        return false;
});

$('#list-with-tradeaction a[href="#list-by-newest"]').click(function(){
        /*
          $('#id_sort option').removeAttr('selected').filter('[value="by-newest"]').attr('selected',true);
          $('#id_action option').removeAttr('selected').filter('[value="sort"]').attr('selected',true);
        */
        $('#id_sort').attr('value','by-newest');
        $('#id_action').attr('value','sort');
        $('#id_page').attr('value',1);
        updatePageTradeaction();
        return false;
});

$('#list-with-tradeaction a[href="#list-by-abc"]').click(function(){
        /*
          $('#id_sort option').removeAttr('selected').filter('[value="by-abc"]').attr('selected',true);
          $('#id_action option').removeAttr('selected').filter('[value="sort"]').attr('selected',true);
        */
        $('#id_sort').attr('value','by-abc');
        $('#id_action').attr('value','sort');
        $('#id_page').attr('value',1);
        updatePageTradeaction();
        return false;
});

$("#list-with-tradeaction a.paginate").click(function(){
        var href = $(this).attr('href');
        var pageNumber = pageNumberFromHREF(href);
        /*
          $('#id_action option').removeAttr('selected').filter('[value="page"]').attr('selected',true);
        */
        $('#id_action').attr('value','page');
        $('#id_page').attr('value',pageNumber);
        updatePageTradeaction();
	return false;
});

$('.mediatype-list li a').click(function(){
        var href = $(this).attr('href');
        var mediatype = href.match(/mediaType=([^&]+)/)[1];

        $('#id_action').attr('value','view');
        $('#id_mediatype').attr('value',mediatype);
        $('#id_page').attr('value',1);
        updatePageTradeaction();
        return false;
});
