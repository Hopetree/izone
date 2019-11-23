//bootstrap4 tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});
//回到顶部
$(window).scroll(function(){
    $('#to-top').hide();
    if ($(window).scrollTop()>=600){
        $('#to-top').show();
    };
});
$("#to-top").click(function () {
        var speed=400;//滑动的速度
        $('body,html').animate({ scrollTop: 0 }, speed);
        return false;
 });
//标题栏鼠标滑过显示下拉
$(function() {
	var $dropdownLi = $('ul.navbar-nav > li.dropdown');
	$dropdownLi.mouseover(function() {
		$(this).addClass('show');
		$(this).children('a.dropdown-toggle').attr('aria-expanded', 'true');
		$(this).children('div.dropdown-menu').addClass('show')
	}).mouseout(function() {
		$(this).removeClass('show');
		$(this).children('a.dropdown-toggle').attr('aria-expanded', 'false');
		$(this).children('div.dropdown-menu').removeClass('show')
	})
});
//锚点平滑移动到指定位置
function TOC_FUN(A) {
	$(A).click(function() {
		$(A).css("color", "#0099ff");
		$(this).css("color", "red");
		$('html, body').animate({
			scrollTop: $($.attr(this, 'href')).offset().top - 55
		}, 500);
		return false
	})
}
$(TOC_FUN('.toc a,.to-com'));

//文章內容图片点击放大，使用bootstrp4的modal模块
$(".article-body img").click(function(){
    var _src = this.src;
    $("#img-to-big img")[0].src = _src;
    $("#img-to-big").modal('show');
})
//添加暗色主题css
function addDarkTheme() {
   var link = document.createElement('link');
   link.type = 'text/css';
   link.id = "theme-css-dark";  // 加上id方便后面好查找到进行删除
   link.rel = 'stylesheet';
   link.href = '/static/blog/css/night.css?20191123.01';
   $("head").append(link);
}
// 删除暗色主题
function removeDarkTheme() {
   $('#theme-css-dark').remove();
}

//切换主题按钮，根据cookies切换主题
$("#theme-img").click(function(){
    var theme_key = "toggleTheme";
    var theme_value = Cookies.get(theme_key);
    if (theme_value == "dark"){
        $("#theme-img").attr("src", "/static/blog/img/toggle-light.png");
        Cookies.set(theme_key, "light", { expires: 180, path: '/' });
        removeDarkTheme();
    } else {
        $("#theme-img").attr("src", "/static/blog/img/toggle-dark.png");
        Cookies.set(theme_key, "dark", { expires: 180, path: '/' });
        addDarkTheme();
    }
})

