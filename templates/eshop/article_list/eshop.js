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

$('a[href="#new-articles-banner"]').click(function(){
        $('#id_banner').attr('value','new-articles');
        $('#id_action').attr('value','banner');
        $('#id_page').attr('value',1);
        return true;
});

$('a[href="#tradeaction-banner"]').click(function(){
        $('#id_banner').attr('value','tradeaction');
        $('#id_action').attr('value','banner');
        $('#id_page').attr('value',1);
        return true;
});

$('a[href="#list-shortly"]').click(function(){
        $('#id_view').attr('value','tabular-view');
        $('#id_action').attr('value','view');
        $('#id_page').attr('value',1);
        updatePageShortly();
        return true;
});

$('a[href="#list"]').click(function(){
        $('#id_view').attr('value','articles');
        $('#id_action').attr('value','view');
        $('#id_page').attr('value',1);
        updatePage();
        return true;
});

$('a[href="#list-with-tradeaction"]').click(function(){
        $('#id_view').attr('value','tradeaction');
        $('#id_action').attr('value','view');
        $('#id_page').attr('value',1);
        updatePageTradeaction();
        return true;
});

