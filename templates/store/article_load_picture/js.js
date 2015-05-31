{% if form.success %}
var articleId = {{ form.instance.pk }};
var articleDetailId = "#article_detail_" + articleId;
console.log("{{form.redirect_to}}");
$.ajax({ type: 'GET',
         url: "{{ form.redirect_to }}",
         success: function(data){
                 $(articleDetailId).replaceWith(data['store/article_detail/detail.html']);
         },
});
{% else %}
$('.article-load-picture').submit(function(event){
        event.preventDefault();
        var form = $(this);
        var formData = $(form).serialize();
        $.ajax({
                type:$(form).attr('method'),
                url: $(form).attr('action'),
                data: formData,
                success: function(data){
                        $(form).parent().html(data['store/article_load_picture/form-body.html']);
                        eval(data['store/article_load_picture/js.js']);
                },
        });
        return false;
})
{% endif %}
