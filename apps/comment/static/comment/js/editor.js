$(function() {
	var simplemde = new SimpleMDE({
		element: document.getElementById("comment-form"),
		insertTexts: {
		horizontalRule: ["", "\n\n-----\n\n"],
		image: ["![图片Alt](http://", ")"],
		link: ["[链接描述](http://", ")"],
		table: ["", "\n\n| Column 1 | Column 2 | Column 3 |\n| -------- | -------- | -------- |\n| Text     | Text      | Text     |\n\n"],
	    },
		toolbar: [{
			name: "bold",
			action: SimpleMDE.toggleBold,
			className: "fa fa-bold",
			title: "粗体",
			"default": !0
		}, {
			name: "italic",
			action: SimpleMDE.toggleItalic,
			className: "fa fa-italic",
			title: "斜体",
			"default": !0
		}, {
			name: "quote",
			action: SimpleMDE.toggleBlockquote,
			className: "fa fa-quote-left",
			title: "引用",
			"default": !0
		}, {
			name: "code",
			action: SimpleMDE.toggleCodeBlock,
			className: "fa fa-code",
			title: "代码"
		}, {
			name: "link",
			action: SimpleMDE.drawLink,
			className: "fa fa-link",
			title: "插入链接",
			"default": !0
		}, {
			name: "image",
			action: SimpleMDE.drawImage,
			className: "fa fa-picture-o",
			title: "插入图片",
			"default": !0
		}, {
			name: "table",
			action: SimpleMDE.drawTable,
			className: "fa fa-table",
			title: "插入表格"
		}, {
			name: "preview",
			action: SimpleMDE.togglePreview,
			className: "fa fa-eye no-disable",
			title: "预览",
			"default": !0
		}, {
			name: "guide",
			action: "http://www.stopfollow.com",
			className: "fa fa-question-circle",
			title: "Markdown语法参考",
			"default": !0
		}],
	});
	$(".editor-statusbar").append("<span class='float-left text-info ml-0 hidden' id='rep-to'></span>");
	$("#editor-footer").append("<button type='button' class='btn btn-danger btn-sm float-right mr-4 hidden' id='no-rep'>取消回复</button>");

	var emoji_tag = $("#emoji-list img");
	emoji_tag.click(function() {
		var e = $(this).data('emoji');
		simplemde.value(simplemde.value()+e);
	});

//    点击回复
	$(".rep-btn").click(function(){
	    simplemde.value('')
	    var u = $(this).data('repuser')
	    var i = $(this).data('repid')
	    sessionStorage.setItem('rep_id',i);
	    $("#rep-to").text("回复 @"+u).removeClass('hidden');
		$("#no-rep").removeClass('hidden');
	});

//    点击取消回复
	$("#no-rep").click(function(){
	    simplemde.value('')
	    sessionStorage.removeItem('rep_id');
	    $("#rep-to").text('').addClass('hidden');
		$("#no-rep").addClass('hidden');
	});

})