function push_spider(CSRF, URL) {
	var url = $('#form-url').val();
	var urls = $('#form-urls').val();
	if (url.length == 0 | urls.length == 0) {
		alert('接口地址和网址链接内容都不能为空！');
		return false
	};
	$.ajaxSetup({
		data: {
			csrfmiddlewaretoken: CSRF
		}
	});
	$('.push-result').html('<i class="fa fa-spinner fa-pulse fa-3x"></i>');
	$.ajax({
		type: 'post',
		url: URL,
		data: {
			'url': url,
			'url_list': urls
		},
		dataType: 'json',
		success: function(ret) {
			$('.push-result').html(ret.msg);
		},
	})
}