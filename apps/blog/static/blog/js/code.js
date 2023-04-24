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
    const copyButton = $('<button>').html('<svg class="m-2" stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" class="h-4 w-4" height="1.2em" width="1.2em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code');
    copyElm.append($('<span class="code-lang">').text(language));
    copyElm.append(copyButton);
    // 添加一个元素取消浮动
    copyElm.append('<div style="clear: both;"></div>');
    $(this).prepend(copyElm);

    const copyBtn = $(this).find('button');
    copyBtn.click(function () {
        copyToClipboard(codeText);
        copyBtn.html('<svg class="m-2" stroke="currentColor" fill="none" stroke-width="2" xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="0 0 24 24"><path d="M9 16.2l-3.6-3.6c-.4-.4-1-.4-1.4 0-.4.4-.4 1 0 1.4l4 4c.2.2.5.3.7.3.3 0 .5-.1.7-.3l8-8c.4-.4.4-1 0-1.4s-1-.4-1.4 0l-7.3 7.3z"/></svg>\nCopied!')
        setTimeout(function () {
            copyBtn.html('<svg class="m-2" stroke="currentColor" fill="none" stroke-width="2" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" height="1.2em" width="1.2em" xmlns="http://www.w3.org/2000/svg"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>Copy code');
        }, 1500);
    });

})
