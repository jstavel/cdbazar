{% if form.success %}
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
{% else %}
$('.item-field-update tbody tr td select, .item-field-update tbody tr td input').focus();
$('.item-field-update').submit(function(event){
        var form = $(this);
        var formData = $(form).serialize();
        event.preventDefault();
        $.ajax({
                type:$(form).attr('method'),
                url: $(form).attr('action'),
                data: formData,
                success: function(data){
                        $(form).parent().html(data['store/item_field_update/form-body.html']);
                        eval(data['store/item_field_update/js.js']);
                },
        });
})
{% endif %}
