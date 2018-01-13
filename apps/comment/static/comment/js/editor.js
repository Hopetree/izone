$(function() {
	var emoji_tag = $("#emoji-list img");
	var f = $("#comment-form");
	emoji_tag.click(function() {
		var e = $(this).data('emoji');
		var t = f.val() + e;
		f.val(t);
		po_Last(f)
	});

});

function po_Last(obj) {
	obj.focus(); //解决ff不获取焦点无法定位问题
	if (window.getSelection) { //ie11 10 9 ff safari
		var max_Len = obj.value.length; //text字符数
		obj.setSelectionRange(max_Len, max_Len);
	} else if (document.selection) { //ie10 9 8 7 6 5
		var range = obj.createTextRange(); //创建range
		range.collapse(false); //光标移至最后
		range.select(); //避免产生空格
	}
}

