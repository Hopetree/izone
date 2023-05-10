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

$('.codehilite').each(function () {
    // 读取代码块语言
    const langClass = $(this).find('pre code').attr('class');
    const language = langClass.replace(/^.*\blanguage-([^ ]+).*$/, '$1') || 'unknown';
    // console.log(language);
    const codeText = $(this).find('pre').text();
    const copyElm = $('<div>').addClass('code-wrapper');
    const copyButton = $('<button>').html('<i class="fa fa-copy mr-2"></i>Copy code');
    const codeShowElm = $('<div class="code-lang">');
    const codeIconElm = $('<i class="fa fa-code mr-2">');
    codeShowElm.append(codeIconElm);
    codeShowElm.append(language);
    copyElm.append(codeShowElm);
    copyElm.append(copyButton);
    // 添加一个元素取消浮动
    copyElm.append('<div style="clear: both;"></div>');
    $(this).prepend(copyElm);

    const copyBtn = $(this).find('button');
    copyBtn.click(function () {
        copyToClipboard(codeText);
        copyBtn.html('<i class="fa fa-clipboard mr-2"></i>Copied!')
        setTimeout(function () {
            copyBtn.html('<i class="fa fa-copy mr-2"></i>Copy code');
        }, 1500);
    });

})
