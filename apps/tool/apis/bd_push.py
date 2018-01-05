import requests


def push_urls(url, urls):
    headers = {
        'User-Agent': 'curl/7.12.1',
        'Host': 'data.zz.baidu.com',
        'Content - Type': 'text / plain',
        'Content - Length': '83'
    }
    try:
        html = requests.post(url, headers=headers, data=urls, timeout=5).text
        return html
    except:
        return '请求超时，请检查链接是否填写错误！'

if __name__ == '__main__':
    url = 'http://data.zz.bidu.com/urls?site=www.stopfollow.com&token=NpU01TxKEtTQAlBV'
    urls = 'http://www.stopfollow.com/tools/wordsearch/'
    ret = push_urls(url,urls)
    print(ret)
