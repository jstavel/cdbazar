$('span.barcode').each(function(){
	var value = $(this).html();
	var element = $(this);
	$.ajax({
		type: 'GET',
		url: '/store/buyout/lookup/?barcode=' + value,
		success: function(data){ 
			element.closest('p.audio3-info').hide().html(data['store/buyout/lookup.html']).fadeIn();
			eval(data['store/js.js']);
		},
	});
});
if( $('form.form2 input[name="choose-article-article_id"][checked="checked"]').length > 0 ){
        $('#id_choose-article-packnumber').focus();
} else {
        $('#id_buyout-barcode').focus();
}
$(".form2-message").delay(2000).fadeOut("slow", function () { $(this).remove(); });
if( $('.load-detail-success').length > 0 ){
        var handler=function(){
                $('form.buyout').submit();
        };
        window.setTimeout(handler,500);
};
