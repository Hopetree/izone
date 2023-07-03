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
