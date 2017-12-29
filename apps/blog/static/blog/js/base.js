//bootstrap4 tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
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