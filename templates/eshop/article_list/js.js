function updatePage(){
        var data = {};
        $(".pagestate").serializeArray().map(function(x){data[x.name] = x.value;});
    	$.ajax({
		type: 'POST',
		url: "/eshop/articles/",
                data: data,
		success: function(data){ 
			$('#list .pagination').html(data['paginator.html']); 
			$('#list .list').html(data['eshop/article_list/list.html']); 
			$('#list .order-by').html(data['eshop/article_list/order-by.html']);
                        $('.mediatype-list').html(data['eshop/mediatype_choose.html']);
			eval(data['eshop/article_list/js.js']);
		},
	});
};

$('#list a[href="#list-by-cheaper"]').click(function(){
        /*
          $('#id_sort option').removeAttr('selected').filter('[value="by-cheaper"]').attr('selected',true);
          $('#id_action option').removeAttr('selected').filter('[value="sort"]').attr('selected',true);
        */
        $('#id_sort').attr('value','by-cheaper');
        $('#id_action').attr('value','sort');
        $('#id_page').attr('value',1).change();
        updatePage();
        return false;
});

$('#list a[href="#list-by-newest"]').click(function(){
        /*
          $('#id_sort option').removeAttr('selected').filter('[value="by-newest"]').attr('selected',true);
          $('#id_action option').removeAttr('selected').filter('[value="sort"]').attr('selected',true);
        */
        $('#id_sort').attr('value','by-newest');
        $('#id_action').attr('value','sort');
        $('#id_page').attr('value',1);
        updatePage();
        return false;
});

$('#list a[href="#list-by-abc"]').click(function(){
        /*
          $('#id_sort option').removeAttr('selected').filter('[value="by-abc"]').attr('selected',true);
          $('#id_action option').removeAttr('selected').filter('[value="sort"]').attr('selected',true);
        */
        $('#id_sort').attr('value','by-abc');
        $('#id_action').attr('value','sort');
        $('#id_page').attr('value',1);
        updatePage();
        return false;
});

$("#list a.paginate").click(function(){
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

$('.mediatype-list li a').click(function(){
        var href = $(this).attr('href');
        var mediatype = href.match(/mediaType=([^&]+)/)[1];
        $('#id_action').attr('value','view');
        $('#id_mediatype').attr('value',mediatype);
        $('#id_page').attr('value',1);
        updatePage();
        return false;
});

$(".list-with-goods a.article-link").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){
			$('.article_detail .modal-body').html(data['eshop/article_detail/detail.html']);
			$('.article_detail').modal().on('shown',function(){
			        eval(data['eshop/article_detail/js.js']);
			        eval(data['eshop/basket/js.js']);
                        });
		},
	});
	return false;
});

