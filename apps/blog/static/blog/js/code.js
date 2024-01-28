function copyToClipboard(text) {
    const temp = $('<div>');
    temp.css({
        position: 'absolute',
        left: '-9999px',
        top: '-9999px'
    }).appendTo($('body'));
    const textarea = $('<textarea>').val(text).appendTo(temp);
    textarea.select();
    // console.log(textarea.val())
    document.execCommand('copy');
    temp.remove();
}

$('.article-body .codehilite').each(function () {
    // 读取代码块语言
    const langClass = $(this).find('pre code').attr('class');
    const language = langClass.replace(/^.*\blanguage-([^ ]+).*$/, '$1') || 'unknown';
    // console.log(language);
    const codeText = $(this).find('pre').text();
    const headElm = $('<div>').addClass('code-wrapper');
    const copyButton = $('<button>').html('Copy');
    const codeShowElm = $('<div class="code-lang">');
    codeShowElm.append(language);
    headElm.append(codeShowElm);
    $(this).prepend(copyButton);
    $(this).prepend(headElm);

    copyButton.click(function () {
        copyToClipboard(codeText);
        copyButton.html('Copied')
        setTimeout(function () {
            copyButton.html('Copy');
        }, 1500);
    });

})

// 等待文档加载完成
$(document).ready(function () {
    // 获取所有 class 为 code-group 的 div 标签
    const codeGroups = $('.code-group');

    // 循环遍历每个 code-group
    codeGroups.each(function () {
        const codeGroupId = "tab-list-" + $(this).attr('id');
        // 创建一个新的 nav 元素
        const divElement = $('<div class="nav nav-tabs" role="tablist"></div>').attr('id', codeGroupId);

        // 获取当前 code-group 下的所有 easy-code 子 div
        const easyCodes = $(this).find('.tab-pane');

        // 循环遍历每个 easy-code
        easyCodes.each(function (index) {
            // 读取 data-code-name 属性的值
            const codeItemId = $(this).attr('id');
            const dataCodeName = $(this).data('code-name');
            const ariaLabelledby = $(this).attr('aria-labelledby');
            const easyA = $('<a data-toggle="tab" role="tab"></a>');
            easyA.attr('id', ariaLabelledby);
            easyA.attr('href', '#' + codeItemId);
            easyA.attr('aria-controls', codeItemId);
            if (index === 0) {
                $(this).addClass('show active');
                easyA.attr('class', 'nav-item nav-link active');
                easyA.attr('aria-selected', 'true');
            } else {
                easyA.attr('class', 'nav-item nav-link')
                easyA.attr('aria-selected', 'false');
            }
            easyA.text(dataCodeName);
            divElement.append(easyA);

            // 打印或使用 dataCodeName
            console.log(dataCodeName);
        });

        // 在当前 code-group 的前面插入新的 nav 元素
        const navElement = $('<nav class="nav-code-group"></nav>');
        navElement.append(divElement);
        $(this).before(navElement);
    });
});
