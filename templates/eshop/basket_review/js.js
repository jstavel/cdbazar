$("a.from-basket").click(function(){
	$.ajax({
		type: 'GET',
		url: $(this).attr('href'),
		success: function(data){ 
			$('.review').html(data['eshop/basket_review/review.html']);
			eval(data['eshop/from_basket/js.js']);
			eval(data['eshop/basket/js.js']);
			eval(data['eshop/basket_rewiew/js.js']);
		},
	});
	return false;
});

function updateDeliveryAddressInputs(){
 	var matchString = "div_id_delivery_";
 	var deliveryElements = $('div').filter(function(index){
		var id = $(this).attr('id');
		if (typeof id === 'undefined'){
			return false;
		};
		return id.substring(0,matchString.length) === matchString;
	});
	var deliveryAddressIsTheSame = typeof $('#id_delivery_is_the_same_as_invoicing').attr('checked') !== 'undefined';
	if( deliveryAddressIsTheSame ){
		deliveryElements.slice(1).fadeOut();
	} else {
		deliveryElements.slice(1).fadeIn();
	};
};
//$('#id_delivery_is_the_same_as_invoicing').change(updateDeliveryAddressInputs);
//updateDeliveryAddressInputs();

function basketUpdate(){
	partDetail = new Object();
	partDetail.name = "update";
	$.ajax({
		type: 'POST',
		url: "/eshop/basket/update/",
		data: $('form.order').serializeArray().concat(partDetail),
		success: function(data){ 
			$('.review').html(data['eshop/basket_review/review.html']);
			eval(data['eshop/basket/js.js']);
			eval(data['eshop/basket_rewiew/js.js']);
		},
	});
	return false;
}
$('#id_delivery_way').change(function(){
	basketUpdate();
});
$('#id_payment_way').change(function(){
	basketUpdate();
});
