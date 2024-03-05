//bootstrap4 tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});
//回到顶部和评论
$(window).scroll(function () {
    const toTop = $('#to-top');
    const toCom = $('#go-to-com');
    const changeTheme = $('#change-theme');
    toTop.hide();
    toCom.hide();
    changeTheme.hide();
    if ($(window).scrollTop() >= 600) {
        toTop.show();
        toCom.show();
        changeTheme.show();
    }
});
$("#to-top").click(function () {
    const speed = 400; //滑动的速度
    $('body,html').animate({
        scrollTop: 0
    }, speed);
    return false;
});
//标题栏鼠标滑过显示下拉
$(function () {
    const $dropdownLi = $('ul.navbar-nav > li.dropdown');
    $dropdownLi.mouseover(function () {
        $(this).addClass('show');
        $(this).children('a.dropdown-toggle').attr('aria-expanded', 'true');
        $(this).children('div.dropdown-menu').addClass('show')
    }).mouseout(function () {
        $(this).removeClass('show');
        $(this).children('a.dropdown-toggle').attr('aria-expanded', 'false');
        $(this).children('div.dropdown-menu').removeClass('show')
    })
});

//锚点平滑移动到指定位置
function TOC_FUN(A) {
    $(A).click(function () {
        const href = $(this).attr('href');
        // $(A).css("color", "#0099ff");
        // $(this).css("color", "#10b981");
        // $(this).addClass('active');
        $('html, body').animate({
            scrollTop: $($.attr(this, 'href')).offset().top - 55
        }, 500);
        history.pushState(null, null, href); // 更新URL，显示 #
    })
    return true
}

$(TOC_FUN('.toc a,.to-com,#go-to-com,.subject-topic-li a'));

//文章內容图片点击放大，使用bootstrap4的modal模块
$(".article-body img").click(function () {
    $("#img-to-big img")[0].src = this.src;
    $("#img-to-big").modal('show');
})

//添加暗色主题css
function addDarkTheme() {
    let _link = document.getElementById("theme-css-dark")
    if (!_link) {
        const link = document.createElement('link');
        link.type = 'text/css';
        link.id = "theme-css-dark"; // 加上id方便后面好查找到进行删除
        link.rel = 'stylesheet';
        link.href = '/static/blog/css/night.css?v=' + css_night_version;
        $("head").append(link);
    }
    const changeThemeI = $('#change-theme i');
    changeThemeI.removeClass('fa-moon-o');
    changeThemeI.addClass('fa-sun-o');
}

// 删除暗色主题
function removeDarkTheme() {
    $('#theme-css-dark').remove();
    const changeThemeI = $('#change-theme i');
    changeThemeI.removeClass('fa-sun-o');
    changeThemeI.addClass('fa-moon-o');
}

//切换主题按钮，根据cookies切换主题
$("#change-theme").click(function () {
    const theme_key = "toggleTheme";
    const theme_value = Cookies.get(theme_key);
    if (theme_value === "dark") {
        Cookies.set(theme_key, "light", {
            expires: 3,
            path: '/'
        });
        removeDarkTheme();
    } else {
        Cookies.set(theme_key, "dark", {
            expires: 3,
            path: '/'
        });
        addDarkTheme();
    }
})

// 页面到某个标题则将标题高亮
$(document).ready(function () {
    $(window).scroll(function () {
        const scrollPos = $(document).scrollTop();
        // 遍历每个导航链接
        $('.toc ul li a').each(function () {
            const target = $(this).attr('href');

            // 检查滚动位置与目标节的位置关系
            if ($(target).length && $(target).offset().top <= scrollPos + 56) {
                // 移除所有导航链接的激活状态
                $('.toc ul li a').removeClass('active');
                // 为当前可见的目标节的导航链接添加激活状态
                $(this).addClass('active');
            }
        });
        // 获取评论区的位置，如果到了评论区则取消所有导航的active
        const commentBlock = $('#comment-block');
        if ($(commentBlock).length && $(commentBlock).offset().top <= scrollPos + 200) {
            // 移除所有导航链接的激活状态
            $('.toc ul li a').removeClass('active');
        }
    });
});