//get url params
var getParam = function(name){
    var search = document.location.search;
    var pattern = new RegExp("[?&]"+name+"\=([^&]+)", "g");
    var matcher = pattern.exec(search);
    var items = null;
    if(null != matcher){
            try{
                    items = decodeURIComponent(decodeURIComponent(matcher[1]));
            }catch(e){
                    try{
                            items = decodeURIComponent(matcher[1]);
                    }catch(e){
                            items = matcher[1];
                    }
            }
    }
    return items;
};

//baidu links push api
function push_spider(CSRF, URL) {
	var url = $.trim($('#form-url').val());
	var urls = $.trim($('#form-urls').val());
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
	var url = $.trim($('#form-url').val());
	var map_url = $.trim($('#form-sitemap').val());
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

//regex api
function regex_api(CSRF, URL) {
	var r = $.trim($('#form-regex').val());
	var texts = $.trim($('#form-text').val());
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
			'texts': texts,
			'key':getParam('key')
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

//docker search
function docker_search(CSRF, URL) {
	var name = $.trim($('#image-name').val());
	if (name.length == 0) {
		alert('待查询的镜像名称不能为空！');
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
			'name': name,
		},
		dataType: 'json',
		success: function(ret) {
		    var _code = ret['status'];
		    if (_code != 200) {
                var newhtml = '<div class="my-2">' + ret['error'] + '</div>';
                $('.push-result').html(newhtml);
                return
		    };
		    var _results = ret['results'];
		    var newhtml = '<table class="table table-bordered my-0"><thead class="thead-light"><tr><th scope="col">镜像版本</th>' +
		        '<th scope="col">镜像大小</th><th scope="col">更新时间</th></tr></thead><tbody>';
            for (var i=0;i < _results.length; i++) {
                newhtml += '<tr><th scope="row">' + _results[i]['name'] + '</th><td>' + _results[i]['full_size'] + '</td><td>' +
                    _results[i]['last_updated'] + '</td></tr>'
            }
		    newhtml += '</tbody></table>'
			$('.push-result').html(newhtml);
		},
	})
}