//baidu links push api
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

//sitemap urls baidu push api
function site_push_spider(CSRF, URL) {
	var url = $('#form-url').val();
	var map_url = $('#form-sitemap').val();
	if (url.length == 0 | map_url.length == 0) {
		alert('接口地址和sitemap地址内容都不能为空！');
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
			'map_url': map_url
		},
		dataType: 'json',
		success: function(ret) {
			$('.push-result').html(ret.msg);
		},
	})
}

//link test api
function link_test_spider(CSRF, URL) {
	var p = $('#form-info').val();
	var urls = $('#form-links').val();
	if (p.length == 0 | urls.length == 0) {
		alert('需要检查的信息和友链地址都不能为空！');
		return false
	};
	$.ajaxSetup({
		data: {
			csrfmiddlewaretoken: CSRF
		}
	});
	$('.push-result').html('<i class="fa fa-spinner fa-pulse fa-3x my-3"></i>');
	$.ajax({
		type: 'post',
		url: URL,
		data: {
			'p': p,
			'urls': urls
		},
		dataType: 'json',
		success: function(ret) {
		    var tab = '<table class="table"><thead class="thead-light"><tr><th scope="col">友情链接</th>' +
                '<th scope="col">状态</th></tr></thead><tbody>'
            for (var i in ret){
                tab += '<tr><th scope="row">' + i + '</th><td>' + ret[i] + '</td></tr>'
            }
            tab += '</tbody></table>'
			$('.push-result').html(tab);
		},
	})
}

//regex api
function regex_api(CSRF, URL) {
	var r = $('#form-regex').val();
	var texts = $('#form-text').val();
	if (r.length == 0 | texts.length == 0) {
		alert('待提取信息和正则表达式都不能为空！');
		return false
	};
	$.ajaxSetup({
		data: {
			csrfmiddlewaretoken: CSRF
		}
	});
	$('.push-result').html('<i class="fa fa-spinner fa-pulse fa-3x my-3"></i>');
	$.ajax({
		type: 'post',
		url: URL,
		data: {
			'r': r,
			'texts': texts
		},
		dataType: 'json',
		success: function(ret) {
		    var newhtml = '<div class="text-left re-result">' + ret.result + "</div>"
			$('.push-result').html(newhtml);
		},
	})
}

//user-agent api
function useragent_api(CSRF, URL) {
    var d_tags = $("#device_type input:checkbox:checked");
    var os_tags = $("#os input:checkbox:checked");
    var n_tags = $("#navigator input:checkbox:checked");
    var d_lis = new Array();
    var os_lis = new Array();
    var n_lis = new Array();
    if (d_tags.length > 0){
        for (var i=0;i<d_tags.length;i++){
            d_lis.push(d_tags[i].value);
        }
    };
    if (os_tags.length > 0){
        for (var i=0;i<os_tags.length;i++){
            os_lis.push(os_tags[i].value);
        }
    };
    if (n_tags.length > 0){
        for (var i=0;i<n_tags.length;i++){
            n_lis.push(n_tags[i].value);
        }
    };
	$.ajaxSetup({
		data: {
			csrfmiddlewaretoken: CSRF
		}
	});
	$.ajax({
		type: 'post',
		url: URL,
		data: {
		    'd_lis': d_lis.join(),
			'os_lis': os_lis.join(),
			'n_lis': n_lis.join()
		},
		dataType: 'json',
		success: function(ret) {
			$('.push-result').text(ret.result)
		},
	})
}