$("li.new-article").click(function(){
        var article_detail_href = $(this).find('a.article-link').attr('href');
        $.ajax({
		type: 'GET',
		url: article_detail_href,
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
