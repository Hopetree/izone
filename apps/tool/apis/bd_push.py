import requests
import re

def push_urls(url, urls):
    '''根据百度站长提供的API推送链接'''
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
        return "{'error':404,'message':'请求超时，接口地址错误！'}"

def get_urls(url):
    '''提取网站sitemap中所有链接，参数必须是sitemap的链接'''
    try:
        html = requests.get(url,timeout=5).text
    except:
        return 'miss'
    else:
        urls = re.findall('<loc>\s*?(.*?)\s*?</loc>', html)
        return '\n'.join(urls)


if __name__ == '__main__':
    url = 'www.stopfollow-sh_8i.com'
    u = re.findall(r'(http|https://.*?)/.*?', url)
    home_url = u[0] if u else url
    print(home_url)