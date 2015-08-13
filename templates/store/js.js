$('a.new-window').click(function(){
        window.open(this.href);
        return false;
});
$('a.load-detail').click(function(){
	var href = $(this).attr('href');
	var element = $(this);
	$.ajax({
		type: 'GET',
		url: href,
		success: function(data){ 
			var result = data['store/buyout/load_detail.html'];
			if( result.indexOf('error:') == -1){
				element.closest('td').hide().html("<span class='text-success'>" + data['store/buyout/load_detail.html'] + "</span>").fadeIn();
			} else {
				element.closest('td').hide().append("<span class='text-error'>" + data['store/buyout/load_detail.html'] + "</span>").fadeIn();
			}
			eval(data['store/buyout/js.js']);
		},
	});
        element.fadeOut();
	return false;
});
