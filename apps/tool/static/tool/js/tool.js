//禁用按钮一段时间后自动启用
function disableButton(button,t=5000) {
    // 禁用按钮
    button.prop("disabled", true);

    // t毫秒后启用按钮
    setTimeout(function() {
        button.prop("disabled", false);
    }, t);
}
//get url params
var getParam = function (name) {
    var search = document.location.search;
    var pattern = new RegExp("[?&]" + name + "\=([^&]+)", "g");
    var matcher = pattern.exec(search);
    var items = null;
    if (null != matcher) {
        try {
            items = decodeURIComponent(decodeURIComponent(matcher[1]));
        } catch (e) {
            try {
                items = decodeURIComponent(matcher[1]);
            } catch (e) {
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
    }
    ;
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
        success: function (ret) {
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
    }
    ;
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
        success: function (ret) {
            $('.push-result').html(ret.msg);
        },
    })
}

//regex api
function regex_api(CSRF, URL) {
    var max_word = 50000;
    var r = $.trim($('#form-regex').val());
    var texts = $.trim($('#form-text').val());
    if (r.length == 0 | texts.length == 0) {
        alert('待提取信息和正则表达式都不能为空！');
        return false
    }
    ;
    if (texts.length > max_word) {
        alert('文本长度超过限制：' + texts.length + '/' + max_word);
        return false
    }
    ;
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
            'key': getParam('key')
        },
        dataType: 'json',
        success: function (ret) {
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
    if (d_tags.length > 0) {
        for (var i = 0; i < d_tags.length; i++) {
            d_lis.push(d_tags[i].value);
        }
    }
    ;
    if (os_tags.length > 0) {
        for (var i = 0; i < os_tags.length; i++) {
            os_lis.push(os_tags[i].value);
        }
    }
    ;
    if (n_tags.length > 0) {
        for (var i = 0; i < n_tags.length; i++) {
            n_lis.push(n_tags[i].value);
        }
    }
    ;
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
        success: function (ret) {
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
    }
    ;
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
        success: function (ret) {
            if (!ret.error) {
                var newhtml = '<table class="table table-bordered my-0"><thead class="thead-light"><tr><th scope="col">镜像版本</th>' +
                    '<th scope="col">镜像大小</th><th scope="col">更新时间</th></tr></thead><tbody>';
                for (var i = 0; i < ret.results.length; i++) {
                    var item = ret.results[i]
                    newhtml += '<tr><th scope="row">' + item.name + '</th><td>' + item.full_size + '</td><td>' + item.last_updated + '</td></tr>'
                }
                newhtml += '</tbody></table>'
            } else {
                var newhtml = '<div class="my-2">' + ret.error + '</div>';
            }
            $('.push-result').html(newhtml);
        },
        error: function (XMLHttpRequest) {
            var _code = XMLHttpRequest.status;
            if (_code == 404) {
                var error_text = '镜像仓库没有查询到相关信息，请检查镜像名称后重试！';
            } else if (_code == 500) {
                var error_text = '请求超时，请稍后重试！'
            } else {
                var error_text = '未知错误...'
            }
            var newhtml = '<div class="my-2">' + error_text + '</div>';
            $('.push-result').html(newhtml);
        }
    })
}

//docker search from docker hub
function docker_search_from_hub() {
    let repo_name;
    const name = $.trim($('#image-name').val());
    if (name.length === 0) {
        alert('待查询的镜像名称不能为空！');
        return false
    }
    if (name.indexOf("/") >= 0) {
        repo_name = name;
    } else {
        repo_name = 'library/' + name;
    }
    const url = 'https://registry.hub.docker.com/v2/repositories/' + repo_name + '/tags/';
    $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (ret) {
            let new_html = '<table class="table table-bordered my-0"><thead class="thead-light"><tr><th scope="col">镜像版本</th>' +
                '<th scope="col">镜像大小</th><th scope="col">更新时间</th></tr></thead><tbody>';
            for (let i = 0; i < ret.results.length; i++) {
                const item = ret.results[i];
                new_html += '<tr><th scope="row">' + item.name + '</th><td>' + item["full_size"] + '</td><td>' + item["last_updated"] + '</td></tr>'
            }
            new_html += '</tbody></table>'
            $('.push-result').html(new_html);
        },
        error: function (xhr) {
            let new_html;
            if (xhr.status === 404) {
                new_html = '<div class="my-2">' + '查询镜像信息异常' + '</div>';
            } else {
                console.log(xhr.responseText);
                const responseText = xhr.responseText; // 获取接口返回的错误信息
                const errorData = JSON.parse(responseText); // 转换为JavaScript对象
                new_html = '<div class="my-2">' + errorData['message'] + '</div>';
            }
            $('.push-result').html(new_html);
        }

    })
}

// word cloud
function word_cloud(CSRF, URL, max_word) {
    var text = $.trim($('#form-text').val());
    if (text.length == 0) {
        alert('待统计文本内容不能为空！');
        return false
    }
    ;
    if (text.length > max_word) {
        alert('文本长度超过限制：' + text.length + '/' + max_word);
        return false
    }
    ;
    var stop_text = $.trim($('#stop-text').val());
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
            'text': text,
            'stop_text': stop_text
        },
        dataType: 'json',
        success: function (ret) {
            if (ret.code == 0) {
                Highcharts.chart('show-wc', {
                    series: [{
                        type: 'wordcloud',
                        data: ret.data.list
                    }],
                    title: {
                        text: '词云图'
                    }
                });
            } else {
                var newhtml = '<div class="p-3">' + ret.error + '</div>';
                $('.push-result').html(newhtml);
            }
        },
        error: function (XMLHttpRequest) {
            var newhtml = '<div class="p-3">服务器异常，未知错误</div>';
            $('.push-result').html(newhtml)
        }
    })
}

// ip查询
function query_ip_from_baidu() {
    const result_div = $('#result');
    const ip = $.trim($('#query-ip').val());
    result_div.addClass('text-center');
    if (ip.length === 0) {
        const new_html = '<div class="my-2">' + 'IP缺失' + '</div>';
        result_div.html(new_html);
        return false
    }
    result_div.html('<i class="fa fa-spinner fa-pulse fa-3x my-3"></i>');
    const save_ip_key = 'save.query.ip.' + ip;
    const cookie_ip_info = Cookies.get(save_ip_key);
    if (cookie_ip_info !== undefined) {
        result_div.removeClass('text-center');
        console.info(cookie_ip_info);
        const ret = JSON.parse(cookie_ip_info);
        let new_html = '<div class="my-2">';
        // 得到归属地，国家到区，去重显示
        const lst = [ret.data["continent"], ret.data.country,
            ret.data["prov"], ret.data.city, ret.data["district"]];
        const new_lst = [...new Set(lst)];
        const address = new_lst.join(' ')
        new_html += '<p>' + '<strong>归属地：</strong>' + address + '</p>';
        // 经营商
        new_html += '<p>' + '<strong>经营商：</strong>' + ret.data["isp"] + '</p>';
        // 经纬度
        new_html += '<p>' + '<strong>经纬度：</strong>' + ret.data["lng"] + ',' + ret.data["lat"] + '</p>';
        // 邮编
        new_html += '<p>' + '<strong>邮&emsp;编：</strong>' + ret.data.zipcode + '</p>';
        new_html += '</div>';
        result_div.html(new_html);
    } else {
        const url = 'https://qifu-api.baidubce.com/ip/geo/v1/district?ip=' + encodeURIComponent(ip)
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'json',
            success: function (ret) {
                let new_html = '<div class="my-2">';
                if (ret.code === 'Success') {
                    result_div.removeClass('text-center');
                    console.log(ret)
                    // 结果存到cookie，保留1天
                    Cookies.set(save_ip_key, JSON.stringify(ret), {expires: 1, path: '/'});
                    // 得到归属地，国家到区，去重显示
                    const lst = [ret.data["continent"], ret.data.country,
                        ret.data["prov"], ret.data.city, ret.data["district"]];
                    const new_lst = [...new Set(lst)];
                    const address = new_lst.join(' ')
                    new_html += '<p>' + '<strong>归属地：</strong>' + address + '</p>';
                    // 经营商
                    new_html += '<p>' + '<strong>经营商：</strong>' + ret.data["isp"] + '</p>';
                    // 经纬度
                    new_html += '<p>' + '<strong>经纬度：</strong>' + ret.data["lng"] + ',' + ret.data["lat"] + '</p>';
                    // 邮编
                    new_html += '<p>' + '<strong>邮&emsp;编：</strong>' + ret.data.zipcode + '</p>';
                } else {
                    new_html += ret["msg"]
                }
                new_html += '</div>';
                result_div.html(new_html);
            },
            error: function (xhr) {
                let new_html;
                if (xhr.status === 404) {
                    new_html = '<div class="my-2">' + '查询IP信息异常' + '</div>';
                } else {
                    console.log(xhr.responseText)
                    const responseText = xhr.responseText; // 获取接口返回的错误信息
                    const errorData = JSON.parse(responseText); // 转换为JavaScript对象
                    new_html = '<div class="my-2">' + errorData['msg'] + '</div>';
                }
                result_div.html(new_html);
            }
        })
    }
}

function disable_query_ip() {
    // 请求成功则添加cookie，同时禁用请求按钮
    const query_ip_key = 'queryIP';
    // 获取当前时间
    const currentDate = new Date();
    // 设置cookie过期时间为1分钟后
    const expirationDate = new Date(currentDate.getTime() + 60 * 1000);
    Cookies.set(query_ip_key, "disabled", {expires: expirationDate, path: '/'});
    // 将请求按钮设置成不可用
    const send_btn = $('#start-post');
    send_btn.prop("disabled", true);
    send_btn.attr('title', '查询不可用，两次查询时间需间隔1分钟')
}