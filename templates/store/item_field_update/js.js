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
                        $('.item_edit .modal-body').html(data['store/item_field_update/form.html']);
                        $('.item_edit').modal();
                },
        });
});
