function article_update_save(csrf, api_url, article_slug) {
    const article_body = testEditor.getMarkdown();
    $.ajaxSetup({
        data: {
            csrfmiddlewaretoken: csrf
        }
    });
    $.ajax({
        type: 'post',
        url: api_url,
        data: {
            'article_slug': article_slug,
            'article_body': article_body,
        },
        dataType: 'json',
        success: function (data) {
            if (data.code === 0) {
                window.location.href = data.data.callback
            }
        },
    })
}